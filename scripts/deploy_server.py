#!/usr/bin/env python3
"""Deploy TG-Monitoring to the remote server from the local workspace (SFTP + SSH)."""

from __future__ import annotations

import pathlib
import stat
import sys

try:
    import paramiko
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

ROOT = pathlib.Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    ".playwright",
}
SKIP_FILES = {".env"}  # root .env has deploy/github secrets — upload api/.env only


def load_env(path: pathlib.Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def run(ssh: paramiko.SSHClient, cmd: str, timeout: int = 900) -> str:
    print(f"$ {cmd}")
    _stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=timeout)
    chunks: list[str] = []
    for line in iter(stdout.readline, ""):
        safe = line.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        try:
            print(safe, end="")
        except UnicodeEncodeError:
            print(safe.encode("ascii", errors="replace").decode("ascii"), end="")
        chunks.append(line)
    code = stdout.channel.recv_exit_status()
    err = stderr.read().decode("utf-8", errors="ignore")
    if err.strip():
        try:
            print(err)
        except UnicodeEncodeError:
            print(err.encode("ascii", errors="replace").decode("ascii"))
    if code != 0:
        raise RuntimeError(f"Command failed ({code}): {cmd}")
    return "".join(chunks)


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote: str) -> None:
    parts = remote.strip("/").split("/")
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def should_skip(path: pathlib.Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    if any(p in SKIP_DIRS for p in rel_parts):
        return True
    if path.name in SKIP_FILES and path.parent == ROOT:
        return True
    if path.name.endswith(".pyc"):
        return True
    return False


def upload_tree(sftp: paramiko.SFTPClient, deploy_path: str) -> None:
    ensure_remote_dir(sftp, deploy_path)
    for path in ROOT.rglob("*"):
        if should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        remote = f"{deploy_path}/{rel}"
        if path.is_dir():
            ensure_remote_dir(sftp, remote)
            continue
        ensure_remote_dir(sftp, str(pathlib.PurePosixPath(remote).parent))
        print(f"upload {rel}")
        sftp.put(str(path), remote)


def main() -> None:
    env = load_env(ROOT / ".env")
    host = env["DEPLOY_HOST"]
    user = env.get("DEPLOY_USER", "root")
    password = env["DEPLOY_PASSWORD"]
    deploy_path = env.get("DEPLOY_PATH", "/opt/tg-monitoring")

    api_env_path = ROOT / "apps" / "api" / ".env"
    api_env = api_env_path.read_text(encoding="utf-8")
    if f"http://{host}" not in api_env:
        api_env = api_env.rstrip() + f"\nAPI_CORS_ORIGINS=http://{host},http://localhost:5173\n"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {user}@{host} ...")
    ssh.connect(hostname=host, username=user, password=password, timeout=45)

    run(ssh, "export DEBIAN_FRONTEND=noninteractive; apt-get update -y")
    run(
        ssh,
        "export DEBIAN_FRONTEND=noninteractive; apt-get install -y "
        "curl ca-certificates python3 python3-venv python3-pip "
        "nginx docker.io docker-compose-v2 build-essential",
    )

    # Node.js 22 via NodeSource if missing
    run(
        ssh,
        "if ! command -v node >/dev/null 2>&1; then "
        "curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && "
        "apt-get install -y nodejs; fi; node -v; npm -v",
    )
    run(ssh, "systemctl enable --now docker || true")

    run(ssh, f"mkdir -p {deploy_path}")
    sftp = ssh.open_sftp()
    upload_tree(sftp, deploy_path)
    with sftp.file(f"{deploy_path}/apps/api/.env", "w") as fh:
        fh.write(api_env)
    sftp.close()

    run(ssh, f"cd {deploy_path} && (docker compose up -d postgres || docker-compose up -d postgres)")

    run(
        ssh,
        f"cd {deploy_path}/apps/api && "
        f"python3 -m venv .venv && "
        f".venv/bin/pip install -U pip && "
        f".venv/bin/pip install -e '.[dev]' && "
        f".venv/bin/playwright install --with-deps chromium",
        timeout=1800,
    )

    run(ssh, f"cd {deploy_path}/apps/web && npm install && npm run build", timeout=900)

    api_unit = f"""[Unit]
Description=TG-Monitoring API
After=network.target docker.service

[Service]
Type=simple
WorkingDirectory={deploy_path}/apps/api
EnvironmentFile={deploy_path}/apps/api/.env
ExecStart={deploy_path}/apps/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    nginx_conf = f"""server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    root {deploy_path}/apps/web/dist;
    index index.html;

    location /api/ {{
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }}

    location /health {{
        proxy_pass http://127.0.0.1:8000/health;
    }}

    location / {{
        try_files $uri $uri/ /index.html;
    }}
}}
"""

    sftp = ssh.open_sftp()
    with sftp.file("/etc/systemd/system/tg-monitoring-api.service", "w") as fh:
        fh.write(api_unit)
    with sftp.file("/etc/nginx/sites-available/tg-monitoring", "w") as fh:
        fh.write(nginx_conf)
    sftp.close()

    run(ssh, "ln -sfn /etc/nginx/sites-available/tg-monitoring /etc/nginx/sites-enabled/tg-monitoring")
    run(ssh, "rm -f /etc/nginx/sites-enabled/default")
    run(ssh, "nginx -t && systemctl reload nginx")
    run(ssh, "systemctl daemon-reload && systemctl enable --now tg-monitoring-api && systemctl restart tg-monitoring-api")
    run(ssh, "systemctl --no-pager --full status tg-monitoring-api | sed -n '1,25p'")
    run(ssh, "curl -sS http://127.0.0.1:8000/health || true")
    run(ssh, f"curl -sS -o /dev/null -w '%{{http_code}}\\n' http://127.0.0.1/ || true")

    ssh.close()
    print(f"\nDeployed. Open http://{host}/")


if __name__ == "__main__":
    main()
