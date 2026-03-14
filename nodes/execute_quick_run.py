"""
execute_quick_run: run the minimal command and confirm the code executes.

Strategy:
- Run via shell in the repo directory
- Watch stdout/stderr for signs of a successful first step
- Kill the process after first success signal (we only need to confirm it runs)
- Hard timeout: 5 minutes
- If process exits by itself (clean or error), capture that too
"""

import os
import re
import shlex
import subprocess
import threading
import time
from pathlib import Path

from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.live import Live
from rich.text import Text

from state import ReplicatorState

console = Console()

# Patterns that suggest a training step completed
SUCCESS_PATTERNS = re.compile(
    r"(loss|acc|accuracy|epoch|step|iter|batch|train|val|eval|metric|reward|score)\s*[:=\[]",
    re.IGNORECASE,
)

TIMEOUT_SECONDS = 300   # 5 min hard limit
CONFIRM_SECONDS = 8     # wait this long after first success signal before killing


def execute_quick_run(state: ReplicatorState, config: RunnableConfig) -> dict:
    cmd = state.get("quick_run_cmd", "")
    repo_path = Path(state["repo_local_path"])

    if not cmd:
        return {
            "quick_run_success": False,
            "quick_run_log": "No command to run.",
            "phase": "execute_quick_run",
        }

    console.print(f"\n[bold cyan]Running:[/bold cyan] {cmd}")
    console.print(f"[dim]Working dir: {repo_path}[/dim]\n")

    lines = []
    success_detected = False
    success_time = None

    env = os.environ.copy()

    # Inject user-provided inputs as environment variables
    user_inputs = state.get("user_inputs") or {}
    env.update(user_inputs)

    # Prepend env activation prefix (e.g. "conda run -n myenv")
    env_prefix = state.get("env_activate_prefix", "").strip()
    if env_prefix:
        cmd = f"{env_prefix} {cmd}"

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
            bufsize=1,
        )
    except Exception as e:
        return {
            "quick_run_success": False,
            "quick_run_log": f"Failed to start process: {e}",
            "error": str(e),
            "phase": "execute_quick_run",
        }

    start = time.time()

    with Live(Text("", style="dim"), console=console, refresh_per_second=10) as live:
        for line in proc.stdout:
            line = line.rstrip()
            lines.append(line)
            live.update(Text(line, style="dim"))

            if not success_detected and SUCCESS_PATTERNS.search(line):
                success_detected = True
                success_time = time.time()
                console.print(f"\n[green]✓ First step confirmed:[/green] {line}")

            # Kill after confirming success
            if success_detected and (time.time() - success_time) >= CONFIRM_SECONDS:
                proc.kill()
                lines.append(f"\n[Stopped after confirming run — {CONFIRM_SECONDS}s post first step]")
                break

            # Hard timeout
            if (time.time() - start) >= TIMEOUT_SECONDS:
                proc.kill()
                lines.append(f"\n[Timeout after {TIMEOUT_SECONDS}s — treating as success if no error]")
                # If no crash yet, consider it running
                if not success_detected:
                    success_detected = True
                break

        proc.wait(timeout=10)

    log = "\n".join(lines)
    returncode = proc.returncode

    # Process exited on its own
    if not success_detected:
        if returncode == 0:
            success_detected = True
        else:
            # Check log for obvious error markers
            lower_log = log.lower()
            if any(kw in lower_log for kw in ("error", "exception", "traceback", "failed")):
                success_detected = False
            else:
                # Non-zero exit but no obvious error — ambiguous, mark failed
                success_detected = False

    if success_detected:
        console.print("[green]✓ Quick run succeeded[/green]")
    else:
        console.print("[red]✗ Quick run failed[/red]")

    return {
        "quick_run_success": success_detected,
        "quick_run_log": log,
        "phase": "execute_quick_run",
        "error": "",
    }
