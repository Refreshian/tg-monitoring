#!/usr/bin/env python3
"""Deploy query-rewrite feature and related frontend to production."""

from __future__ import annotations

import pathlib
import time

import paramiko

ROOT = pathlib.Path(__file__).resolve().parents[1]

FILES = [
    "apps/api/app/core/config.py",
    "apps/api/app/schemas/preview.py",
    "apps/api/app/services/preview_service.py",
    "apps/api/app/services/query_rewrite_service.py",
    "apps/api/.env.example",
    "apps/web/src/pages/PreviewPage.tsx",
    "apps/web/src/types/preview.ts",
    "apps/web/src/features/preview/QueryRewriteNotice.tsx",
    "apps/web/src/styles/global.css",
]


def load_env() -> dict[str, str]:
    data: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def ensure_dir(sftp: paramiko.SFTPClient, remote: str) -> None:
    parts = remote.strip("/").split("/")
    cur = ""
    for part in parts:
        cur += "/" + part
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def merge_env(sftp: paramiko.SFTPClient, updates: dict[str, str]) -> None:
    remote = "/opt/tg-monitoring/apps/api/.env"
    with sftp.file(remote, "r") as fh:
        text = fh.read().decode("utf-8")
    lines = text.splitlines()
    existing: dict[str, str] = {}
    other: list[str] = []
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            existing[key] = line
        else:
            other.append(line)
    for key, value in updates.items():
        existing[key] = f"{key}={value}"
    out = other + [existing[k] for k in existing]
    # Keep deterministic-ish: comments first then keys
    with sftp.file(remote, "w") as fh:
        fh.write("\n".join(out).rstrip() + "\n")


def run(ssh: paramiko.SSHClient, cmd: str, timeout: int = 300) -> int:
    print("$", cmd)
    _, out, _ = ssh.exec_command(cmd, get_pty=True, timeout=timeout)
    start = time.time()
    while True:
        if out.channel.recv_ready():
            print(out.channel.recv(4096).decode("utf-8", errors="replace"), end="")
        if out.channel.exit_status_ready() and not out.channel.recv_ready():
            break
        if time.time() - start > timeout:
            raise TimeoutError(cmd)
        time.sleep(0.15)
    while out.channel.recv_ready():
        print(out.channel.recv(4096).decode("utf-8", errors="replace"), end="")
    return out.channel.recv_exit_status()


def main() -> None:
    env = load_env()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        env["DEPLOY_HOST"],
        username=env["DEPLOY_USER"],
        password=env["DEPLOY_PASSWORD"],
        timeout=45,
    )
    sftp = ssh.open_sftp()
    for rel in FILES:
        remote = f"/opt/tg-monitoring/{rel}"
        ensure_dir(sftp, str(pathlib.PurePosixPath(remote).parent))
        sftp.put(str(ROOT / rel), remote)
        print("uploaded", rel)

    merge_env(
        sftp,
        {
            "AITUNNEL_API_KEY": env["AITUNNEL_API_KEY"],
            "AITUNNEL_BASE_URL": env.get("AITUNNEL_BASE_URL", "https://api.aitunnel.ru/v1"),
            "AITUNNEL_MODEL": env.get("AITUNNEL_MODEL", "auto"),
            "AITUNNEL_MAX_TOKENS": env.get("AITUNNEL_MAX_TOKENS", "800"),
        },
    )
    print("env merged")
    sftp.close()

    code = run(ssh, "cd /opt/tg-monitoring/apps/web && npm run build", timeout=180)
    if code != 0:
        raise SystemExit(code)
    run(ssh, "systemctl restart tg-monitoring-api")
    time.sleep(2)
    run(
        ssh,
        "cd /opt/tg-monitoring/apps/api && .venv/bin/python -c "
        "\"import asyncio; from app.services.query_rewrite_service import QueryRewriteService; "
        "print(asyncio.run(QueryRewriteService().rewrite('Сидни Суини')))\"",
        timeout=90,
    )
    ssh.close()
    print("DONE")


if __name__ == "__main__":
    main()
