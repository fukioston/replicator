"""
Task index — tracks all repos Replicator has worked on.
Stored as tasks.json inside workspace_dir.
"""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def _tasks_file(workspace_dir: str) -> Path:
    p = Path(workspace_dir).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p / "tasks.json"


def load_tasks(workspace_dir: str) -> dict:
    f = _tasks_file(workspace_dir)
    if not f.exists():
        return {}
    return json.loads(f.read_text())


def save_tasks(workspace_dir: str, tasks: dict):
    _tasks_file(workspace_dir).write_text(json.dumps(tasks, ensure_ascii=False, indent=2))


def upsert_task(workspace_dir: str, repo_name: str, updates: dict):
    tasks = load_tasks(workspace_dir)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if repo_name not in tasks:
        tasks[repo_name] = {"created_at": now}
    tasks[repo_name].update(updates)
    tasks[repo_name]["updated_at"] = now
    save_tasks(workspace_dir, tasks)


def show_task(workspace_dir: str, task_name: str):
    tasks = load_tasks(workspace_dir)
    t = tasks.get(task_name)
    if not t:
        console.print(f"[red]Task '{task_name}' not found.[/red]")
        return
    from rich.panel import Panel
    from rich.markdown import Markdown
    lines = [
        f"**Name:** {task_name}",
        f"**Repo:** {t.get('repo_url', '—')}",
        f"**Status:** {t.get('status', '—')}",
        f"**Phase:** {t.get('phase', '—')}",
        f"**Created:** {t.get('created_at', '—')}",
        f"**Updated:** {t.get('updated_at', '—')}",
    ]
    if t.get("introduction"):
        lines += ["", "**Introduction:**", t["introduction"]]
    if t.get("quick_run_cmd"):
        lines += ["", f"**Quick run cmd:** `{t['quick_run_cmd']}`"]
    if t.get("error"):
        lines += ["", f"**Error:** {t['error']}"]
    if t.get("diagnosis"):
        lines += ["", "**Diagnosis:**", t["diagnosis"]]
    console.print(Panel(Markdown("\n".join(lines)), title=f"Task: {task_name}"))


def list_tasks(workspace_dir: str):
    tasks = load_tasks(workspace_dir)
    if not tasks:
        console.print("[yellow]No tasks yet. Use `replicator create -n <name> --repo <url>` to start one.[/yellow]")
        return

    table = Table(title="Replicator Tasks", show_lines=True)
    table.add_column("Repo", style="cyan", no_wrap=True)
    table.add_column("URL", style="dim")
    table.add_column("Phase", style="green")
    table.add_column("Status")
    table.add_column("Updated")
    table.add_column("Introduction", max_width=50)

    status_color = {
        "done": "[green]done[/green]",
        "in_progress": "[yellow]in_progress[/yellow]",
        "failed": "[red]failed[/red]",
    }

    for name, t in tasks.items():
        status = t.get("status", "unknown")
        table.add_row(
            name,
            t.get("repo_url", ""),
            t.get("phase", "—"),
            status_color.get(status, status),
            t.get("updated_at", "—"),
            (t.get("introduction", "") or "")[:100],
        )

    console.print(table)
