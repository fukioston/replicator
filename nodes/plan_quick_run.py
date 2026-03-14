"""
plan_quick_run: LLM decides the minimal command to verify the project runs.
"""

import json
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from rich.console import Console

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import PLAN_QUICK_RUN_SYSTEM, PLAN_QUICK_RUN_USER

console = Console()


def plan_quick_run(state: ReplicatorState, config: RunnableConfig) -> dict:
    replicator_config = config["configurable"]["replicator_config"]
    llm = build_llm(replicator_config)

    reproduction_plan = state.get("reproduction_plan") or []
    plan_str = "\n".join(
        f"{s['step']}. {s['action']}" + (f": {s['command']}" if s.get("command") else "")
        for s in reproduction_plan
    ) or "(no plan)"

    file_contents = state.get("file_contents") or {}
    contents_str = "\n\n".join(
        f"=== {path} ===\n{content}" for path, content in file_contents.items()
    ) or "(none)"

    prompt = PLAN_QUICK_RUN_USER.format(
        repo_url=state["repo_url"],
        train_entrypoint=state.get("train_entrypoint") or "(unknown)",
        reproduction_plan=plan_str,
        file_contents=contents_str,
    )

    with console.status("[cyan]Planning minimal run command...[/cyan]"):
        response = llm.invoke([
            SystemMessage(content=PLAN_QUICK_RUN_SYSTEM),
            HumanMessage(content=prompt),
        ])

    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
    except (json.JSONDecodeError, IndexError) as e:
        return {"error": f"plan_quick_run: invalid JSON from LLM: {e}", "phase": "plan_quick_run"}

    cmd = data.get("cmd", "")
    cwd = data.get("cwd", ".")
    env_vars = data.get("env_vars") or {}
    rationale = data.get("rationale", "")

    # Embed cwd into cmd string as a prefix if non-trivial
    full_cmd = cmd
    if cwd and cwd != ".":
        full_cmd = f"cd {cwd} && {cmd}"

    # Serialize env_vars into the cmd for storage/display
    if env_vars:
        env_prefix = " ".join(f"{k}={v}" for k, v in env_vars.items())
        full_cmd = f"{env_prefix} {full_cmd}"

    console.print(f"[cyan]Quick run command:[/cyan] {full_cmd}")
    if rationale:
        console.print(f"[dim]{rationale}[/dim]")

    return {
        "quick_run_cmd": full_cmd,
        "phase": "plan_quick_run",
        "error": "",
    }
