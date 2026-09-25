"""Local Web UX and API Server for BlogForge.

Provides a responsive web interface to:
1. Browse, view, and live-lint posts with score meter and style findings.
2. Edit markdown and front matter directly in the browser.
3. Review and publish posts with one click.
4. Generate new style-matched posts with choice of LLM backend.
5. Schedule automated generations and publication jobs.
6. Check Git status, stage, commit, and push directly to GitHub/remote.

Zero dependencies: built entirely on standard library http.server.
"""

from __future__ import annotations

import datetime
import http.server
import json
import socketserver
import threading
import urllib.parse
from pathlib import Path
from typing import Any

from . import corpus, generator, gitops, linter, providers, scheduler, site, topics, voice

STATIC_DIR = Path(__file__).parent / "ui"
class BlogForgeRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving JSON API endpoints and static SPA files."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path.startswith("/api/"):
            self._handle_api_get(path, urllib.parse.parse_qs(url.query))
            return

        # Serve index.html for SPA routes if not a specific file
        file_path = STATIC_DIR / path.lstrip("/")
        if not file_path.is_file() and not path.startswith("/assets"):
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path.startswith("/api/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            body: dict[str, Any] = {}
            if body_bytes:
                try:
                    body = json.loads(body_bytes.decode("utf-8"))
                except Exception:
                    body = {}
            self._handle_api_post(path, body)
            return

        self._send_json({"error": "Not Found"}, status=404)

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)


    def _handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
        try:
            if path == "/api/status":
                git_info = gitops.get_git_status()
                sched_info = scheduler.load_schedule()
                self._send_json({
                    "git": git_info,
                    "scheduler": sched_info,
                    "post_count": len(corpus.iter_posts()),
                })

            elif path == "/api/providers":
                cfg = site.load_config()
                provs = providers.available_providers(cfg)
                self._send_json({"providers": provs})

            elif path == "/api/posts":
                posts = []
                for p in corpus.iter_posts():
                    meta = dict(p.front)
                    rel_path = p.rel_path()
                    posts.append({
                        "path": rel_path,
                        "title": p.title,
                        "section": p.section,
                        "date": p.date_str,
                        "draft": p.draft,
                        "reviewed": p.reviewed,
                        "aiAssisted": p.ai_assisted,
                        "words": p.words,
                    })
                posts.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
                self._send_json({"posts": posts})

            elif path == "/api/posts":
                posts = []
                for p in corpus.iter_posts():
                    meta = dict(p.metadata)
                    # Normalize string paths for web
                    rel_path = str(p.path.relative_to(site.ROOT)).replace("\\", "/")
                    posts.append({
                        "path": rel_path,
                        "title": p.title,
                        "section": p.section,
                        "date": p.date,
                        "draft": meta.get("draft", False),
                        "reviewed": meta.get("reviewed", False),
                        "aiAssisted": meta.get("aiAssisted", False),
                        "words": len(p.body.split()),
                    })
                posts.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
                self._send_json({"posts": posts})

            elif path == "/api/post":
                rel = query.get("path", [""])[0]
                full_path = (site.ROOT / rel).resolve()
                if not full_path.exists() or not str(full_path).startswith(str(site.CONTENT_DIR)):
                    self._send_json({"error": "Invalid post path"}, status=400)
                    return
                post = corpus.load_post(full_path)
                if not post:
                    self._send_json({"error": "Post not found"}, status=404)
                    return
                cfg = site.load_config()
                prof = voice.load_profile(cfg["profile"])
                report = linter.lint_post(post, prof)
                self._send_json({
                    "path": rel,
                    "metadata": post.front,
                    "body": post.body,
                    "content": full_path.read_text(encoding="utf-8"),
                    "linter": report.as_dict(),
                })

            elif path == "/api/topics":
                data = topics.load()
                posts = corpus.iter_posts()
                ranked = topics.rank(data, posts, limit=20)
                self._send_json({"topics": ranked})

            elif path == "/api/topics":
                data = topics.load(site.TOPICS_FILE)
                posts = corpus.iter_posts()
                ranked = topics.rank(data, posts, limit=20)
                self._send_json({"topics": ranked})

                self._send_json({
                    "path": rel,
                    "metadata": post.metadata,
                    "body": post.body,
                    "content": full_path.read_text(encoding="utf-8"),
                    "linter": report.as_dict(),
                })

            elif path == "/api/topics":
                data = topics.load(site.TOPICS_FILE)
                ranked = topics.rank_topics(data)
                self._send_json({"topics": ranked})

            elif path == "/api/schedule":
                self._send_json(scheduler.load_schedule())

            elif path == "/api/git/status":
                self._send_json(gitops.get_git_status())

            else:
                self._send_json({"error": "Endpoint not found"}, status=404)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, status=500)

    def _handle_api_post(self, path: str, body: dict[str, Any]) -> None:
        try:
            if path == "/api/lint":
                content = body.get("content", "")
                section = body.get("section", "sysadmin")
                cfg = site.load_config()
                prof = voice.load_profile(cfg["profile"])
                report = linter.lint_text(content, prof, section=section)
                self._send_json(report.as_dict())

            elif path == "/api/post/save":
                rel = body.get("path", "")
                content = body.get("content", "")
                full_path = (site.ROOT / rel).resolve()
                if not str(full_path).startswith(str(site.CONTENT_DIR)):
                    self._send_json({"error": "Path must be inside content/"}, status=400)
                    return
                full_path.write_text(content, encoding="utf-8")
                post = corpus.load_post(full_path)
                cfg = site.load_config()
                prof = voice.load_profile(cfg["profile"])
                report = linter.lint_post(post, prof) if post else None
                self._send_json({
                    "ok": True,
                    "message": "Saved successfully",
                    "linter": report.as_dict() if report else None,
                })

            elif path == "/api/post/review":
                rel = body.get("path", "")
                full_path = (site.ROOT / rel).resolve()
                unapprove = bool(body.get("unapprove", False))
                publish = bool(body.get("publish", False))
                generator.review(full_path, approve=not unapprove, publish=publish)
                self._send_json({"ok": True, "reviewed": not unapprove, "published": publish})

            elif path == "/api/post/publish":
                rel = body.get("path", "")
                full_path = (site.ROOT / rel).resolve()
                generator.review(full_path, approve=True, publish=True)
                self._send_json({"ok": True, "message": f"Published {rel}"})

            else:
                self._handle_api_post_extended(path, body)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, status=500)





    def _handle_api_post_extended(self, path: str, body: dict[str, Any]) -> None:
        if path == "/api/generate":
            brief = {
                "title": body.get("title", ""),
                "section": body.get("section", "sysadmin"),
                "tags": [t.strip() for t in body.get("tags", "").split(",") if t.strip()],
                "facts": body.get("facts", ""),
            }
            if body.get("topic_id"):
                topics_data = topics.load(site.TOPICS_FILE)
                found = topics.find(topics_data, body["topic_id"])
                if found:
                    brief = dict(found)
            provider = body.get("provider", "auto")
            model = body.get("model") or None
            write = not bool(body.get("dry_run", False))
            draft = generator.generate(
                brief=brief,
                section=brief.get("section", "sysadmin"),
                provider=provider,
                model=model,
                write=write,
            )
            rel_path = str(draft.path.relative_to(site.ROOT)).replace("\\", "/") if draft.path else None
            score = draft.lint.score if draft.lint else None
            self._send_json({
                "ok": True,
                "path": rel_path,
                "score": score,
                "attempts": draft.attempts,
                "content": draft.text,
            })

        elif path == "/api/schedule/add":
            job = scheduler.add_job(
                action=body.get("action", "generate"),
                topic=body.get("topic", ""),
                topic_id=body.get("topic_id", ""),
                section=body.get("section", "sysadmin"),
                provider=body.get("provider", "auto"),
                model=body.get("model", ""),
                run_at=body.get("run_at", ""),
                recurring=body.get("recurring", ""),
                auto_push=bool(body.get("auto_push", False)),
            )
            self._send_json({"ok": True, "job": job})

        elif path == "/api/schedule/toggle":
            data = scheduler.load_schedule()
            data["enabled"] = not data.get("enabled", False)
            scheduler.save_schedule(data)
            self._send_json({"ok": True, "enabled": data["enabled"]})

        elif path == "/api/schedule/delete":
            job_id = body.get("id", "")
            deleted = scheduler.delete_job(job_id)
            self._send_json({"ok": deleted})

        elif path == "/api/schedule/run-now":
            job_id = body.get("id", "")
            data = scheduler.load_schedule()
            target_job = next((j for j in data.get("jobs", []) if j.get("id") == job_id), None)
            if not target_job:
                self._send_json({"error": "Job not found"}, status=404)
                return
            scheduler.run_job(target_job)
            scheduler.save_schedule(data)
            self._send_json({"ok": True, "job": target_job})

        elif path == "/api/git/commit":
            msg = body.get("message", "BlogForge: Update content")
            paths = body.get("paths", None)
            res = gitops.stage_and_commit(msg, paths)
            self._send_json(res)
        elif path == "/api/git/push":
            remote = body.get("remote", "origin")
            branch = body.get("branch", None)
            res = gitops.push_to_remote(remote, branch)
            self._send_json(res)

        else:
            self._send_json({"error": "Endpoint not found"}, status=404)

def start_server(host: str = "127.0.0.1", port: int = 8765, daemon: bool = True, open_browser: bool = True) -> None:
    """Start the BlogForge local web server and background scheduler daemon."""
    import webbrowser
    if daemon:
        scheduler_daemon = scheduler.SchedulerDaemon()
        scheduler_daemon.start()

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server_address = (host, port)
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, BlogForgeRequestHandler) as httpd:
        url = f"http://{host}:{port}/"
        print(f"BlogForge UX running at {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down BlogForge server...")
            if daemon:
                scheduler_daemon.stop()

run_server = start_server

def run_server(port: int = 8765, daemon: bool = True) -> None:
    """Start the BlogForge local web server and background scheduler daemon."""
    if daemon:
        scheduler_daemon = scheduler.SchedulerDaemon()
        scheduler_daemon.start()

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server_address = ("", port)
    
    # Enable address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, BlogForgeRequestHandler) as httpd:
        print(f"BlogForge UX running at http://localhost:{port}/")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down BlogForge server...")
            if daemon:
                scheduler_daemon.stop()


