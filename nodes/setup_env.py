"""
setup_env: install repo dependencies into the current Python environment.
"""

import subprocess
import sys
from pathlib import Path

from langchain_core.runnables import RunnableConfig
from rich.console import Console

from state import ReplicatorState

console = Console()


def setup_env(state: ReplicatorState, config: RunnableConfig) -> dict:
    repo_path = Path(state["repo_local_path"])
    logs = []

    install_targets = []
    for req_file in ["requirements.txt", "requirements-dev.txt"]:
        if (repo_path / req_file).exists():
            install_targets.append(("-r", req_file))

    has_package = (repo_path / "setup.py").exists() or (repo_path / "pyproject.toml").exists()

    if not install_targets and not has_package:
        console.print("[dim]No requirements file found, skipping env setup.[/dim]")
        return {"env_setup_log": "(no requirements file found)", "env_ready": True, "phase": "setup_env"}

    with console.status("[cyan]Installing dependencies...[/cyan]"):
        for flag, target in install_targets:
            cmd = [sys.executable, "-m", "pip", "install", flag, target, "--quiet", "--no-warn-script-location"]
            logs.append(f"$ pip install {flag} {target}")
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=300)
            if result.stdout.strip():
                logs.append(result.stdout.strip())
            if result.stderr.strip():
                logs.append(result.stderr.strip())

        if has_package:
            cmd = [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet", "--no-warn-script-location"]
            logs.append("$ pip install -e .")
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=300)
            if result.stdout.strip():
                logs.append(result.stdout.strip())
            if result.stderr.strip():
                logs.append(result.stderr.strip())

    console.print("[green]✓ Environment ready[/green]")
    return {
        "env_setup_log": "\n".join(logs),
        "env_ready": True,
        "phase": "setup_env",
    }
