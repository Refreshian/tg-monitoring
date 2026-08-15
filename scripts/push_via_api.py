#!/usr/bin/env python3
"""Push local main branch to GitHub using the Git Data API (works with fine-grained PATs)."""

from __future__ import annotations

import base64
import hashlib
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request
import json

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_env() -> dict[str, str]:
    data: dict[str, str] = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def api(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "tg-monitoring-deploy",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"{method} {url} -> {exc.code}: {detail}") from exc


def git_files() -> list[str]:
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files"],
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def main() -> None:
    env = load_env()
    token = env["GITHUB_TOKEN"]
    owner = env["GITHUB_USER"]
    repo = "tg-monitoring"
    base = f"https://api.github.com/repos/{owner}/{repo}"

    files = git_files()
    print(f"Uploading {len(files)} files via GitHub API...")

    tree_items = []
    for rel in files:
        path = ROOT / rel
        content = path.read_bytes()
        # Skip large binaries if any
        blob = api(
            "POST",
            f"{base}/git/blobs",
            token,
            {
                "content": base64.b64encode(content).decode("ascii"),
                "encoding": "base64",
            },
        )
        tree_items.append(
            {
                "path": rel.replace("\\", "/"),
                "mode": "100644",
                "type": "blob",
                "sha": blob["sha"],
            }
        )
        print(f"  blob {rel}")

    tree = api("POST", f"{base}/git/trees", token, {"tree": tree_items})
    print("tree", tree["sha"])

    # Get current main SHA if exists
    parent = None
    try:
        ref = api("GET", f"{base}/git/ref/heads/main", token)
        parent = ref["object"]["sha"]
        print("parent", parent)
    except RuntimeError as exc:
        if "404" not in str(exc):
            raise
        print("No main branch yet")

    commit_payload: dict = {
        "message": "Initial TG-Monitoring scaffold: React site, FastAPI preview API, Brand Analytics automation.",
        "tree": tree["sha"],
    }
    if parent:
        commit_payload["parents"] = [parent]

    commit = api("POST", f"{base}/git/commits", token, commit_payload)
    print("commit", commit["sha"])

    if parent:
        api(
            "PATCH",
            f"{base}/git/refs/heads/main",
            token,
            {"sha": commit["sha"], "force": True},
        )
    else:
        api(
            "POST",
            f"{base}/git/refs",
            token,
            {"ref": "refs/heads/main", "sha": commit["sha"]},
        )

    print(f"Pushed: https://github.com/{owner}/{repo}")


if __name__ == "__main__":
    # Ensure git is on PATH for Windows
    main()
