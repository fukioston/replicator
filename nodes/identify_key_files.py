"""
identify_key_files: Phase 1b — ask LLM which files are worth reading.
Cheap call: only README + file tree, no source code yet.
"""

import json
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from rich.console import Console

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import IDENTIFY_FILES_SYSTEM, IDENTIFY_FILES_USER

console = Console()

MAX_FILE_SIZE = 8000  # chars per file


def identify_key_files(state: ReplicatorState, config: RunnableConfig) -> dict:
    replicator_config = config["configurable"]["replicator_config"]
    llm = build_llm(replicator_config)

    prompt = IDENTIFY_FILES_USER.format(
        repo_url=state["repo_url"],
        readme=state["readme"] or "(no README found)",
        file_tree=state["file_tree"],
    )

    with console.status("[cyan]Identifying key files...[/cyan]"):
        response = llm.invoke([
            SystemMessage(content=IDENTIFY_FILES_SYSTEM),
            HumanMessage(content=prompt),
        ])

    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
        key_files = data.get("key_files", [])
        reason = data.get("reason", "")
    except (json.JSONDecodeError, IndexError):
        # Fallback: skip this step
        return {"key_files": [], "file_contents": {}, "phase": "identify_key_files"}

    # Read each key file
    root = Path(state["repo_local_path"])
    file_contents = {}
    found = []
    for rel_path in key_files:
        p = root / rel_path
        if p.exists() and p.is_file():
            content = p.read_text(errors="ignore")[:MAX_FILE_SIZE]
            file_contents[rel_path] = content
            found.append(rel_path)

    console.print(f"[cyan]Key files identified:[/cyan] {', '.join(found)}")
    if reason:
        console.print(f"[dim]{reason}[/dim]")

    return {
        "key_files": found,
        "file_contents": file_contents,
        "phase": "identify_key_files",
    }
