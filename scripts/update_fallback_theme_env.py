"""Update server .env fallback theme and restart API."""

import pathlib
import re
import time

import paramiko

ROOT = pathlib.Path(__file__).resolve().parents[1]
env: dict[str, str] = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    env["DEPLOY_HOST"],
    username=env["DEPLOY_USER"],
    password=env["DEPLOY_PASSWORD"],
    timeout=45,
)
sftp = ssh.open_sftp()
path = "/opt/tg-monitoring/apps/api/.env"
with sftp.open(path, "r") as remote_file:
    text = remote_file.read().decode("utf-8")
text = re.sub(
    r"^BR_ANALYTICS_FALLBACK_THEME_ID=.*$",
    "BR_ANALYTICS_FALLBACK_THEME_ID=14166164",
    text,
    flags=re.M,
)
text = re.sub(
    r"^BR_ANALYTICS_FALLBACK_THEME_NAME=.*$",
    "BR_ANALYTICS_FALLBACK_THEME_NAME=Энергострой",
    text,
    flags=re.M,
)
with sftp.open(path, "w") as remote_file:
    remote_file.write(text.encode("utf-8"))
sftp.close()

_, stdout, _ = ssh.exec_command("grep FALLBACK /opt/tg-monitoring/apps/api/.env")
stdout.channel.recv_exit_status()
print(stdout.read().decode())

_, stdout, _ = ssh.exec_command("systemctl restart tg-monitoring-api")
stdout.channel.recv_exit_status()
time.sleep(1)
print("api restarted")
ssh.close()
