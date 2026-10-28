"""Git operations helper for BlogForge UI and CLI.

Zero external dependencies: wraps git using subprocess with safe defaults.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from . import site


def _run_git(args: list[str], cwd: Path | None = None) -> dict[str, Any]:
    work_dir = cwd or site.ROOT
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(exc)}


def get_git_status() -> dict[str, Any]:
    """Return branch name, remotes, and porcelain status."""
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    status = _run_git(["status", "--porcelain=v1"])
    remotes = _run_git(["remote", "-v"])
    ahead_behind = _run_git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])

    ahead = 0
    behind = 0
    if ahead_behind["ok"] and "\t" in ahead_behind["stdout"]:
        parts = ahead_behind["stdout"].split("\t")
        try:
            ahead = int(parts[0])
            behind = int(parts[1])
        except ValueError:
            pass

    changed_files: list[dict[str, str]] = []
    if status["ok"] and status["stdout"]:
        for line in status["stdout"].splitlines():
            if len(line) >= 4:
                code = line[:2]
                path = line[3:].strip()
                changed_files.append({"status": code, "path": path})

    return {
        "branch": branch["stdout"] if branch["ok"] else "unknown",
        "changed": changed_files,
        "clean": len(changed_files) == 0,
        "ahead": ahead,
        "behind": behind,
        "remotes": remotes["stdout"] if remotes["ok"] else "",
    }


def stage_and_commit(message: str, paths: list[str] | None = None) -> dict[str, Any]:
    """Add specified paths (or all content/posts if None) and commit."""
    if not message.strip():
        return {"ok": False, "error": "Commit message cannot be empty."}

    # If specific paths were given, stage those; otherwise stage content & style/catalog
    if paths:
        stage_args = ["add", "--", *paths]
    else:
        stage_args = ["add", "content", "style", "catalog"]

    add_res = _run_git(stage_args)
    if not add_res["ok"]:
        return {"ok": False, "error": f"git add failed: {add_res['stderr']}"}

    commit_res = _run_git(["commit", "-m", message.strip()])
    if not commit_res["ok"]:
        # If nothing to commit
        if "nothing to commit" in commit_res["stdout"].lower() or "nothing to commit" in commit_res["stderr"].lower():
            return {"ok": True, "message": "Nothing to commit, working tree clean."}
        return {"ok": False, "error": f"git commit failed: {commit_res['stderr'] or commit_res['stdout']}"}

    return {"ok": True, "message": commit_res["stdout"]}


def push_to_remote(remote: str = "origin", branch: str | None = None) -> dict[str, Any]:
    """Push current branch to the specified remote."""
    if not branch:
        branch_res = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_res["stdout"] if branch_res["ok"] else "main"

    res = _run_git(["push", remote, branch])
    if not res["ok"]:
        return {"ok": False, "error": f"git push failed: {res['stderr'] or res['stdout']}"}
    return {"ok": True, "message": res["stderr"] or res["stdout"] or "Push successful"}
