#!/usr/bin/env python3
"""Fast update deploy: sync code, rebuild web, restart API. Does not touch nginx SSL."""

from __future__ import annotations

import pathlib
import time

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
    "agent-transcripts",
    "terminals",
}
SKIP_FILES = {".env"}


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
    start = time.time()
    while True:
        if stdout.channel.recv_ready():
            chunks.append(stdout.channel.recv(4096).decode("utf-8", errors="replace"))
            print(chunks[-1], end="")
        if stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
            break
        if time.time() - start > timeout:
            raise TimeoutError(cmd)
        time.sleep(0.1)
    while stdout.channel.recv_ready():
        chunks.append(stdout.channel.recv(4096).decode("utf-8", errors="replace"))
        print(chunks[-1], end="")
    code = stdout.channel.recv_exit_status()
    if code != 0:
        err = stderr.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Command failed ({code}): {cmd}\n{err}")
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
    if path.name in SKIP_FILES:
        return True
    if path.name.endswith((".pyc", ".png", ".jpg", ".jpeg", ".webp")) and "public" not in rel_parts:
        # still upload public assets
        if "public" not in rel_parts and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            # allow hero in public via not skipping when public in path - handled above
            pass
    if path.name.endswith(".pyc"):
        return True
    return False


def upload_tree(sftp: paramiko.SFTPClient, deploy_path: str) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        # Skip heavy local-only docs dumps etc.
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("scripts/") and rel not in {
            "scripts/deploy_server.py",
            "scripts/update_server.py",
        }:
            # upload scripts folder lightly; skip one-off helpers is fine
            pass
        remote = f"{deploy_path}/{rel}"
        ensure_remote_dir(sftp, str(pathlib.PurePosixPath(remote).parent))
        print(f"upload {rel}")
        sftp.put(str(path), remote)


def merge_api_env_keys(ssh: paramiko.SSHClient, deploy_path: str, keys: dict[str, str]) -> None:
    """Add missing keys to remote apps/api/.env without wiping secrets."""
    remote = f"{deploy_path}/apps/api/.env"
    sftp = ssh.open_sftp()
    try:
        with sftp.file(remote, "r") as fh:
            current = fh.read().decode("utf-8")
    except FileNotFoundError:
        current = ""
    lines = current.splitlines()
    existing = set()
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            existing.add(line.split("=", 1)[0].strip())
    added = []
    for key, value in keys.items():
        if key not in existing:
            lines.append(f"{key}={value}")
            added.append(key)
    if added:
        with sftp.file(remote, "w") as fh:
            fh.write("\n".join(lines).rstrip() + "\n")
        print("Added env keys:", ", ".join(added))
    else:
        print("Remote API .env already has pricing keys")
    sftp.close()


def main() -> None:
    env = load_env(ROOT / ".env")
    host = env["DEPLOY_HOST"]
    user = env.get("DEPLOY_USER", "root")
    password = env["DEPLOY_PASSWORD"]
    deploy_path = env.get("DEPLOY_PATH", "/opt/tg-monitoring")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {user}@{host} ...")
    ssh.connect(hostname=host, username=user, password=password, timeout=45)

    sftp = ssh.open_sftp()
    upload_tree(sftp, deploy_path)
    sftp.close()

    merge_api_env_keys(
        ssh,
        deploy_path,
        {
            "PRICE_QUOTE_DISCOUNT_RATIO": "0.32",
            "BA_TARIFFS_CACHE_DAYS": "30",
        },
    )

    # Ensure CORS includes https domain if missing
    run(
        ssh,
        f"grep -q 'https://tg-monitoring.online' {deploy_path}/apps/api/.env || "
        f"sed -i 's|^API_CORS_ORIGINS=.*|API_CORS_ORIGINS=http://localhost:5173,http://{host},"
        f"http://tg-monitoring.online,https://tg-monitoring.online,"
        f"http://www.tg-monitoring.online,https://www.tg-monitoring.online|' "
        f"{deploy_path}/apps/api/.env",
    )

    run(
        ssh,
        f"cd {deploy_path}/apps/api && "
        f".venv/bin/pip install -e '.[dev]' -q",
        timeout=300,
    )
    run(ssh, f"cd {deploy_path}/apps/web && npm install && npm run build", timeout=900)
    run(ssh, "systemctl restart tg-monitoring-api")
    run(ssh, "systemctl --no-pager --full status tg-monitoring-api | sed -n '1,20p'")
    run(ssh, "curl -sS http://127.0.0.1:8000/health")
    run(
        ssh,
        "test -f /opt/tg-monitoring/apps/api/app/services/pricing.py && "
        "test -f /opt/tg-monitoring/apps/web/src/features/preview/PriceEstimate.tsx && "
        "grep -q estimated_price /opt/tg-monitoring/apps/web/dist/assets/*.js && "
        "echo DEPLOY_OK",
    )

    ssh.close()
    print(f"\nUpdated. Open https://tg-monitoring.online/preview")


if __name__ == "__main__":
    main()
