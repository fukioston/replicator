#!/usr/bin/env python3
"""
Replicator — autonomous ML paper reproduction agent.
Usage:
  python replicator.py --repo https://github.com/author/repo
  python replicator.py --list
"""

import argparse
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from setup_config import load_config
from graph import build_graph
from tasks import upsert_task, list_tasks

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Replicator: autonomous ML paper reproduction agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--repo", help="GitHub repository URL to analyze")
    group.add_argument("--list", action="store_true", help="List all tracked tasks")
    parser.add_argument("--setup", action="store_true", help="Re-run setup wizard")
    args = parser.parse_args()

    # Load or run setup
    if args.setup:
        from setup_config import run_setup
        config = run_setup()
    else:
        config = load_config()

    workspace = str(Path(config["workspace_dir"]).expanduser())

    # --list mode
    if args.list:
        list_tasks(workspace)
        return

    # --repo mode
    repo_url = args.repo
    repo_name = repo_url.rstrip("/").split("/")[-1].removesuffix(".git")

    initial_state = {
        "repo_url": repo_url,
        "workspace_dir": workspace,
        "ssh_host": config.get("ssh_host", ""),
        "ssh_user": config.get("ssh_user", ""),
        "ssh_key_path": config.get("ssh_key_path", ""),
        "remote_workdir": f"{workspace}/runs/{repo_name}",
        "repo_local_path": "",
        "readme": "",
        "requirements": "",
        "file_tree": "",
        "introduction": "",
        "file_breakdown": [],
        "preview": {},
        "reproduction_plan": [],
        "train_entrypoint": "",
        "code_summary": "",
        "env_setup_log": "",
        "env_ready": False,
        "experiments": [],
        "current_experiment_id": 0,
        "heartbeat_count": 0,
        "iteration": 0,
        "max_iterations": config.get("max_iterations", 5),
        "error": "",
        "phase": "",
    }

    graph_config = {
        "configurable": {
            "thread_id": repo_name,
            "replicator_config": config,
        }
    }

    console.print(Panel(f"[bold]Replicator[/bold]\nRepo: {repo_url}", expand=False))

    # Register task as in_progress
    upsert_task(workspace, repo_name, {
        "repo_url": repo_url,
        "status": "in_progress",
        "phase": "starting",
    })

    app = build_graph(workspace)

    try:
        for step in app.stream(initial_state, config=graph_config):
            node = list(step.keys())[0]
            state = step[node]

            if node == "clone_and_read":
                console.print(f"\n[cyan]✓ Cloned[/cyan] → {state.get('repo_local_path', '')}")
                upsert_task(workspace, repo_name, {"phase": "clone_and_read", "status": "in_progress"})

            elif node == "identify_key_files":
                key_files = state.get("key_files") or []
                if key_files:
                    console.print(f"[cyan]✓ Key files:[/cyan] {', '.join(key_files)}")
                upsert_task(workspace, repo_name, {"phase": "identify_key_files", "status": "in_progress"})

            elif node == "analyze_code":
                console.print(f"\n[green]✓ Analysis complete[/green]")
                if state.get("introduction"):
                    console.print(Panel(state["introduction"], title="Introduction"))
                if state.get("file_breakdown"):
                    files_md = "\n\n".join(
                        f"**`{f['path']}`** — {f['role']}\n{f.get('description', '')}"
                        for f in state["file_breakdown"]
                    )
                    console.print(Panel(Markdown(files_md), title="File Breakdown"))
                if state.get("reproduction_plan"):
                    plan_md = "\n".join(
                        f"{s['step']}. **{s['action']}**" + (f"\n   `{s['command']}`" if s.get('command') else "")
                        for s in state["reproduction_plan"]
                    )
                    console.print(Panel(Markdown(plan_md), title="Reproduction Plan"))

                upsert_task(workspace, repo_name, {
                    "phase": "analyze_code",
                    "status": "done",
                    "introduction": (state.get("introduction") or "")[:200],
                })

            elif node == "handle_error":
                console.print(f"\n[red]✗ Error[/red] in phase '{state.get('phase')}': {state.get('error')}")
                upsert_task(workspace, repo_name, {
                    "phase": state.get("phase", ""),
                    "status": "failed",
                    "error": state.get("error", ""),
                })

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        upsert_task(workspace, repo_name, {"status": "in_progress"})


if __name__ == "__main__":
    main()
