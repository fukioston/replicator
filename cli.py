"""
Replicator CLI — entry point for the `replicator` command.
"""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="replicator",
    help="Autonomous ML paper reproduction agent.",
    no_args_is_help=True,
)


def _get_config(run_setup: bool = False) -> dict:
    from setup_config import load_config, run_setup as do_setup
    return do_setup() if run_setup else load_config()


@app.command()
def create(
    name: str = typer.Option(..., "-n", help="Task name"),
    repo: str = typer.Option(..., "--repo", help="GitHub repository URL"),
):
    """Create a new task."""
    from setup_config import load_config
    from tasks import upsert_task, load_tasks

    config = load_config()
    workspace = str(Path(config["workspace_dir"]).expanduser())
    tasks = load_tasks(workspace)

    if name in tasks:
        typer.echo(f"Task '{name}' already exists. Use `replicator run -n {name}` to run it.")
        raise typer.Exit(1)

    upsert_task(workspace, name, {
        "name": name,
        "repo_url": repo,
        "status": "pending",
        "phase": "",
    })
    typer.echo(f"✓ Task '{name}' created → {repo}")
    typer.echo(f"  Run with: replicator run -n {name}")


@app.command()
def run(
    name: str = typer.Option(..., "-n", help="Task name to run"),
):
    """Run analysis for a task."""
    from replicator import run_task
    config = _get_config()
    run_task(name, config)


@app.command(name="list")
def list_cmd():
    """List all tasks."""
    from setup_config import load_config
    from tasks import list_tasks

    config = load_config()
    workspace = str(Path(config["workspace_dir"]).expanduser())
    list_tasks(workspace)


@app.command()
def show(name: str = typer.Argument(..., help="Task name")):
    """Show details of a specific task."""
    from setup_config import load_config
    from tasks import show_task

    config = load_config()
    workspace = str(Path(config["workspace_dir"]).expanduser())
    show_task(workspace, name)


@app.command()
def restart(
    name: str = typer.Option(..., "-n", help="Task name to restart"),
):
    """Restart a task from scratch (creates a new run, preserving history)."""
    from setup_config import load_config
    from tasks import load_tasks, increment_run_id

    config = load_config()
    workspace = str(Path(config["workspace_dir"]).expanduser())

    if name not in load_tasks(workspace):
        typer.echo(f"Task '{name}' not found.")
        raise typer.Exit(1)

    new_id = increment_run_id(workspace, name)
    typer.echo(f"✓ Task '{name}' reset (run #{new_id})")
    typer.echo(f"  Run with: replicator run -n {name}")


@app.command()
def config():
    """Re-run the setup wizard."""
    from setup_config import run_setup
    run_setup()


if __name__ == "__main__":
    app()
