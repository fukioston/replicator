"""
diagnose_error: LLM analyzes why the quick run failed and suggests fixes.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import DIAGNOSE_ERROR_SYSTEM, DIAGNOSE_ERROR_USER

console = Console()

# Show last N chars of log to avoid token overflow
LOG_TAIL = 4000


def diagnose_error(state: ReplicatorState, config: RunnableConfig) -> dict:
    replicator_config = config["configurable"]["replicator_config"]
    output_language = replicator_config.get("output_language", "English")
    llm = build_llm(replicator_config)

    log = state.get("quick_run_log") or ""
    cmd = state.get("quick_run_cmd") or ""

    # Feed only the tail — errors are usually at the end
    log_tail = log[-LOG_TAIL:] if len(log) > LOG_TAIL else log

    system = DIAGNOSE_ERROR_SYSTEM.format(output_language=output_language)
    prompt = DIAGNOSE_ERROR_USER.format(cmd=cmd, log=log_tail)

    with console.status("[cyan]Diagnosing error...[/cyan]"):
        response = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ])

    diagnosis = response.content.strip()
    console.print(Panel(Markdown(diagnosis), title="[red]Error Diagnosis[/red]"))

    return {
        "diagnosis": diagnosis,
        "phase": "diagnose_error",
    }
