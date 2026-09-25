"""Background task scheduling for BlogForge.

Manages scheduled generation and publishing jobs, saving job definitions
in `catalog/schedule.yaml`. Supports scheduled drafting and automated
publishing of human-reviewed drafts on target dates.
"""

from __future__ import annotations

import datetime
import threading
import time
from pathlib import Path
from typing import Any, Callable

from . import corpus, generator, gitops, linter, site, topics, yamlmini

SCHEDULE_FILE = site.CATALOG_DIR / "schedule.yaml"


def load_schedule() -> dict[str, Any]:
    """Load schedule configuration and jobs list."""
    if not SCHEDULE_FILE.exists():
        return {"enabled": False, "interval_minutes": 60, "last_run": None, "jobs": []}
    try:
        raw = yamlmini.parse(SCHEDULE_FILE.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {"enabled": False, "interval_minutes": 60, "last_run": None, "jobs": []}
        raw.setdefault("enabled", False)
        raw.setdefault("interval_minutes", 60)
        raw.setdefault("jobs", [])
        return raw
    except Exception:  # noqa: BLE001
        return {"enabled": False, "interval_minutes": 60, "last_run": None, "jobs": []}


def save_schedule(data: dict[str, Any]) -> None:
    """Save schedule configuration."""
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    text = yamlmini.dump(data)
    SCHEDULE_FILE.write_text(text, encoding="utf-8")

def add_job(
    action: str,
    topic: str = "",
    topic_id: str = "",
    section: str = "sysadmin",
    provider: str = "auto",
    model: str = "",
    run_at: str = "",
    recurring: str = "",
    auto_push: bool = False,
) -> dict[str, Any]:
    """Register a new scheduled job."""
    data = load_schedule()
    job_id = f"job-{int(time.time())}-{len(data.get('jobs', [])) + 1}"
    job = {
        "id": job_id,
        "action": action,
        "topic": topic,
        "topic_id": topic_id,
        "section": section,
        "provider": provider,
        "model": model,
        "run_at": run_at or datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "recurring": recurring,
        "auto_push": auto_push,
        "status": "pending",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "log": "",
    }
    data["jobs"].append(job)
    save_schedule(data)
    return job


def delete_job(job_id: str) -> bool:
    """Remove a job by id."""
    data = load_schedule()
    original_len = len(data.get("jobs", []))
    data["jobs"] = [j for j in data.get("jobs", []) if j.get("id") != job_id]
    if len(data["jobs"]) != original_len:
        save_schedule(data)
        return True
    return False


def run_job(job: dict[str, Any], emit_log: Callable[[str], None] | None = None) -> dict[str, Any]:
    """Execute a single job immediately."""
    def _log(msg: str) -> None:
        if emit_log:
            emit_log(msg)

    action = job.get("action")
    job["status"] = "running"
    job["last_executed"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        if action == "generate":
            _log(f"Starting generation: {job.get('topic') or job.get('topic_id')}")
            brief: dict[str, Any] = {
                "title": job.get("topic") or "",
                "section": job.get("section") or "sysadmin",
            }
            if job.get("topic_id"):
                topics_data = topics.load(site.TOPICS_FILE)
                found = topics.find(topics_data, job["topic_id"])
                if found:
                    brief = dict(found)
            
            draft = generator.generate(
                brief=brief,
                section=job.get("section") or "sysadmin",
                provider=job.get("provider") or "auto",
                model=job.get("model") or None,
                write=True,
            )
            score_str = f"score {draft.lint.score}/100" if draft.lint else "no-lint"
            job["status"] = "completed"
            job["log"] = f"Created {draft.path.name if draft.path else 'draft'} ({score_str})"
            _log(job["log"])

        elif action == "publish_due":
            _log("Publishing reviewed posts due today...")
            published = generator.publish_due(allow_unreviewed=False)
            published_paths = [str(p) for p in published]
            
            job["status"] = "completed"
            job["log"] = f"Published {len(published_paths)} posts"
            _log(job["log"])

            if job.get("auto_push") and published_paths:
                _log("Auto-pushing published posts to git remote...")
                gitops.stage_and_commit(f"Publish due posts: {len(published_paths)} published")
                gitops.push_to_remote()

        elif action == "publish_due":
            _log("Publishing reviewed posts due today...")
            today = datetime.date.today().isoformat()
            published_paths = []
            for post in corpus.iter_posts():
                meta = post.metadata
                post_date = str(meta.get("date", ""))
                is_draft = meta.get("draft") is True
                is_reviewed = meta.get("reviewed") is True
                if is_draft and is_reviewed and post_date <= today:
                    corpus.edit_post(post.path, {"draft": False})
                    published_paths.append(str(post.path))
            
            job["status"] = "completed"
            job["log"] = f"Published {len(published_paths)} posts"
            _log(job["log"])

            if job.get("auto_push") and published_paths:
                _log("Auto-pushing published posts to git remote...")
                gitops.stage_and_commit(f"Publish due posts: {len(published_paths)} published")
                gitops.push_to_remote()

        else:
            job["status"] = "failed"
            job["log"] = f"Unknown action: {action}"

    except Exception as exc:  # noqa: BLE001
        job["status"] = "failed"
        job["log"] = f"Error: {exc}"
        _log(job["log"])

    return job
class SchedulerDaemon:
    """Lightweight in-process background runner for checking pending jobs."""

    def __init__(self, interval_seconds: int = 30) -> None:
        self.interval = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._check_and_execute()
            except Exception:  # noqa: BLE001
                pass
            self._stop_event.wait(self.interval)

    def _check_and_execute(self) -> None:
        data = load_schedule()
        if not data.get("enabled"):
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        jobs = data.get("jobs", [])
        changed = False

        for job in jobs:
            if job.get("status") != "pending":
                continue
            run_at_str = job.get("run_at")
            if not run_at_str:
                continue

            try:
                clean_ts = run_at_str.replace("Z", "+00:00")
                target_time = datetime.datetime.fromisoformat(clean_ts)
                if target_time.tzinfo is None:
                    target_time = target_time.replace(tzinfo=datetime.timezone.utc)
            except Exception:
                continue

            if now >= target_time:
                run_job(job)
                changed = True
                if job.get("recurring") == "daily":
                    job["status"] = "pending"
                    job["run_at"] = (target_time + datetime.timedelta(days=1)).isoformat()
                elif job.get("recurring") == "weekly":
                    job["status"] = "pending"
                    job["run_at"] = (target_time + datetime.timedelta(days=7)).isoformat()

        if changed:
            save_schedule(data)

