"""
gather_user_inputs: interactively ask the user for required external inputs
(API keys, dataset paths, credentials, etc.) identified by plan_quick_run.
"""

from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.prompt import Prompt, Confirm

from state import ReplicatorState

console = Console()


def gather_user_inputs(state: ReplicatorState, config: RunnableConfig) -> dict:
    required_inputs = state.get("required_inputs") or []
    if not required_inputs:
        return {"user_inputs": {}, "phase": "gather_user_inputs"}

    console.print("\n[bold yellow]This project needs some information before running:[/bold yellow]")

    collected = {}

    for item in required_inputs:
        name = item.get("name", "?")
        description = item.get("description", "")
        env_var = item.get("env_var", "")
        required = item.get("required", True)

        label = f"[cyan]{name}[/cyan]"
        if description:
            label += f" [dim]({description})[/dim]"
        if not required:
            label += " [dim][optional, press Enter to skip][/dim]"

        console.print(label)

        # Mask input for anything that looks like a key/token/secret
        is_secret = any(kw in name.lower() or kw in env_var.lower()
                        for kw in ("key", "token", "secret", "password", "credential"))

        value = Prompt.ask(
            f"  {env_var}",
            password=is_secret,
            default="" if not required else ...,
        )

        if value:
            collected[env_var] = value
        elif required:
            console.print(f"[yellow]⚠ Skipped required input '{name}' — run may fail[/yellow]")

    console.print()
    return {"user_inputs": collected, "phase": "gather_user_inputs"}
