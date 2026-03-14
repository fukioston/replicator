"""
Core task runner — called by cli.py.
"""

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from graph import build_graph
from tasks import upsert_task, get_run_id

console = Console()

# Maps the phase that errored → which node to set as_node for resume.
# as_node=X means "resume as if X just finished", so the next node is X's successor.
_PHASE_RESUME_AS_NODE = {
    "identify_key_files": "clone_and_read",
    "analyze_code":       "identify_key_files",
    "setup_env":          "analyze_code",
    "plan_quick_run":     "setup_env",
    "gather_user_inputs": "plan_quick_run",
    "execute_quick_run":  "gather_user_inputs",
    "diagnose_error":     "gather_user_inputs",  # also retry execute
}


def run_task(task_name: str, config: dict):
    """Run the full analysis pipeline for a named task."""
    workspace = str(Path(config["workspace_dir"]).expanduser())
    task = _load_task(workspace, task_name)

    if not task:
        console.print(f"[red]Task '{task_name}' not found. Run `replicator create -n {task_name} --repo <url>` first.[/red]")
        return

    repo_url = task["repo_url"]
    run_id = task.get("run_id", 0)
    thread_id = f"{task_name}_{run_id}"

    graph_config = {
        "configurable": {
            "thread_id": thread_id,
            "replicator_config": config,
        }
    }

    app = build_graph(workspace)

    # -- Check existing checkpoint --
    existing = app.get_state(graph_config)
    if existing.values and existing.values.get("phase"):
        phase = existing.values.get("phase", "")
        error = existing.values.get("error", "")

        if existing.next:
            # Graph was interrupted mid-run (e.g. KeyboardInterrupt) — resume directly
            console.print(Panel(f"[bold]Replicator[/bold]\nTask: {task_name}  |  Repo: {repo_url}\n[yellow]Resuming interrupted run...[/yellow]", expand=False))
            upsert_task(workspace, task_name, {"status": "in_progress"})
            iterator = app.stream(None, config=graph_config)

        elif error:
            # Graph ended with an error — try to resume from the failed phase
            as_node = _PHASE_RESUME_AS_NODE.get(phase)
            if as_node:
                console.print(Panel(
                    f"[bold]Replicator[/bold]\nTask: {task_name}  |  Repo: {repo_url}\n"
                    f"[yellow]Previous run failed at '{phase}'. Resuming from there...[/yellow]",
                    expand=False,
                ))
                app.update_state(graph_config, {"error": ""}, as_node=as_node)
                upsert_task(workspace, task_name, {"status": "in_progress", "error": ""})
                iterator = app.stream(None, config=graph_config)
            else:
                console.print(Panel(f"[bold]Replicator[/bold]\nTask: {task_name}  |  Repo: {repo_url}\n[yellow]Cannot resume from '{phase}', restarting...[/yellow]", expand=False))
                iterator = app.stream(_make_initial_state(task_name, repo_url, workspace, config), config=graph_config)

        else:
            # Graph completed successfully
            console.print(f"[green]Task '{task_name}' already completed.[/green]")
            console.print("Use [cyan]replicator restart -n {task_name}[/cyan] to run again from scratch.")
            return
    else:
        # No checkpoint — fresh start
        console.print(Panel(f"[bold]Replicator[/bold]\nTask: {task_name}  |  Repo: {repo_url}", expand=False))
        upsert_task(workspace, task_name, {"status": "in_progress", "phase": "starting"})
        iterator = app.stream(_make_initial_state(task_name, repo_url, workspace, config), config=graph_config)

    # -- Stream nodes --
    try:
        for step in iterator:
            node = list(step.keys())[0]
            state = step[node]

            if node == "clone_and_read":
                console.print(f"\n[cyan]✓ Cloned[/cyan] → {state.get('repo_local_path', '')}")
                upsert_task(workspace, task_name, {"phase": "clone_and_read", "status": "in_progress"})

            elif node == "identify_key_files":
                key_files = state.get("key_files") or []
                if key_files:
                    console.print(f"[cyan]✓ Key files:[/cyan] {', '.join(key_files)}")
                upsert_task(workspace, task_name, {"phase": "identify_key_files", "status": "in_progress"})

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
                upsert_task(workspace, task_name, {
                    "phase": "analyze_code",
                    "status": "in_progress",
                    "introduction": (state.get("introduction") or "")[:200],
                })

            elif node == "setup_env":
                upsert_task(workspace, task_name, {"phase": "setup_env", "status": "in_progress"})

            elif node == "plan_quick_run":
                console.print(f"[cyan]Quick run command:[/cyan] {state.get('quick_run_cmd', '')}")
                upsert_task(workspace, task_name, {"phase": "plan_quick_run", "status": "in_progress"})

            elif node == "gather_user_inputs":
                upsert_task(workspace, task_name, {"phase": "gather_user_inputs", "status": "in_progress"})

            elif node == "execute_quick_run":
                success = state.get("quick_run_success", False)
                status = "done" if success else "failed"
                upsert_task(workspace, task_name, {
                    "phase": "execute_quick_run",
                    "status": status,
                    "quick_run_cmd": state.get("quick_run_cmd", ""),
                    "quick_run_success": success,
                })

            elif node == "diagnose_error":
                upsert_task(workspace, task_name, {
                    "phase": "diagnose_error",
                    "status": "failed",
                    "diagnosis": (state.get("diagnosis") or "")[:500],
                })

            elif node == "handle_error":
                console.print(f"\n[red]✗ Error[/red] in phase '{state.get('phase')}': {state.get('error')}")
                upsert_task(workspace, task_name, {
                    "phase": state.get("phase", ""),
                    "status": "failed",
                    "error": state.get("error", ""),
                })

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Run again to resume.[/yellow]")
        upsert_task(workspace, task_name, {"status": "in_progress"})


def _make_initial_state(task_name: str, repo_url: str, workspace: str, config: dict) -> dict:
    return {
        "repo_url": repo_url,
        "workspace_dir": workspace,
        "ssh_host": config.get("ssh_host", ""),
        "ssh_user": config.get("ssh_user", ""),
        "ssh_key_path": config.get("ssh_key_path", ""),
        "remote_workdir": f"{workspace}/runs/{task_name}",
        "repo_local_path": "",
        "readme": "",
        "requirements": "",
        "file_tree": "",
        "key_files": [],
        "file_contents": {},
        "introduction": "",
        "file_breakdown": [],
        "preview": {},
        "reproduction_plan": [],
        "train_entrypoint": "",
        "code_summary": "",
        "env_setup_log": "",
        "env_ready": False,
        "env_activate_prefix": "",
        "quick_run_cmd": "",
        "required_inputs": [],
        "user_inputs": {},
        "quick_run_log": "",
        "quick_run_success": False,
        "diagnosis": "",
        "experiments": [],
        "current_experiment_id": 0,
        "heartbeat_count": 0,
        "iteration": 0,
        "max_iterations": config.get("max_iterations", 5),
        "error": "",
        "phase": "",
    }


def _load_task(workspace: str, task_name: str) -> dict:
    from tasks import load_tasks
    return load_tasks(workspace).get(task_name, {})
