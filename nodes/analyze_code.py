"""
analyze_code: LLM analyzes the repo and produces:
- introduction: what this project is
- file_breakdown: per-file explanation
- preview: key files and architecture
- reproduction_plan: step-by-step plan
- train_entrypoint: path to training script
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.live import Live
from rich.text import Text

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import ANALYZE_REPO_SYSTEM, ANALYZE_REPO_USER

console = Console()


def analyze_code(state: ReplicatorState, config: RunnableConfig) -> dict:
    replicator_config = config["configurable"]["replicator_config"]
    llm = build_llm(replicator_config)
    output_language = replicator_config.get("output_language", "English")

    system = ANALYZE_REPO_SYSTEM.format(output_language=output_language)
    prompt = ANALYZE_REPO_USER.format(
        repo_url=state["repo_url"],
        readme=state["readme"] or "(no README found)",
        file_tree=state["file_tree"],
        requirements=state["requirements"] or "(no requirements file found)",
    )

    # Stream tokens and display live
    full_text = ""
    console.print("\n[bold cyan]Analyzing repository...[/bold cyan]")
    with Live(Text("", style="dim"), console=console, refresh_per_second=15) as live:
        for chunk in llm.stream([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]):
            full_text += chunk.content
            # Show last 300 chars so terminal doesn't flood
            preview = full_text[-300:].lstrip()
            live.update(Text(preview, style="dim"))

    try:
        text = full_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
    except (json.JSONDecodeError, IndexError) as e:
        return {"error": f"LLM returned invalid JSON: {e}", "phase": "analyze"}

    return {
        "introduction": data.get("introduction", ""),
        "file_breakdown": data.get("file_breakdown", []),
        "preview": data.get("preview", {}),
        "reproduction_plan": data.get("reproduction_plan", []),
        "train_entrypoint": data.get("train_entrypoint", ""),
        "code_summary": json.dumps(data, ensure_ascii=False, indent=2),
        "error": "",
        "phase": "analyze_code",
    }
