"""
setup_env: LLM reads README and generates environment setup commands, then executes them.
Supports conda, venv, and plain pip workflows.
"""

import json
import subprocess
import sys
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from rich.console import Console

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import SETUP_ENV_SYSTEM, SETUP_ENV_USER

console = Console()


def setup_env(state: ReplicatorState, config: RunnableConfig) -> dict:
    replicator_config = config["configurable"]["replicator_config"]
    llm = build_llm(replicator_config)
    repo_path = Path(state["repo_local_path"])

    # List requirements files present
    req_names = [
        name for name in [
            "requirements.txt", "requirements-dev.txt",
            "environment.yml", "environment.yaml",
            "setup.py", "pyproject.toml",
        ]
        if (repo_path / name).exists()
    ]
    req_files_str = "\n".join(req_names) if req_names else "(none found)"

    prompt = SETUP_ENV_USER.format(
        readme=state.get("readme") or "(no README found)",
        req_files=req_files_str,
    )

    with console.status("[cyan]Planning environment setup...[/cyan]"):
        response = llm.invoke([
            SystemMessage(content=SETUP_ENV_SYSTEM),
            HumanMessage(content=prompt),
        ])

    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
    except (json.JSONDecodeError, IndexError) as e:
        return {"error": f"setup_env: invalid JSON from LLM: {e}", "phase": "setup_env"}

    commands = data.get("commands", [])
    python_prefix = data.get("python_prefix", "")
    notes = data.get("notes", "")

    if notes:
        console.print(f"[dim]{notes}[/dim]")

    if not commands:
        console.print("[dim]No setup commands needed.[/dim]")
        return {"env_setup_log": "", "env_ready": True, "env_activate_prefix": "", "phase": "setup_env"}

    logs = []
    with console.status("[cyan]Setting up environment...[/cyan]"):
        for cmd in commands:
            console.print(f"[dim]$ {cmd}[/dim]")
            logs.append(f"$ {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.stdout.strip():
                logs.append(result.stdout.strip())
            if result.stderr.strip():
                logs.append(result.stderr.strip())
            if result.returncode != 0:
                console.print(f"[yellow]⚠ Command exited {result.returncode} (continuing)[/yellow]")

    console.print(f"[green]✓ Environment ready[/green]" + (f" (prefix: {python_prefix})" if python_prefix else ""))
    return {
        "env_setup_log": "\n".join(logs),
        "env_ready": True,
        "env_activate_prefix": python_prefix,
        "phase": "setup_env",
        "error": "",
    }
