"""
analyze_code: LLM analyzes the repo and produces:
- introduction: what this project is
- preview: key files and architecture
- reproduction_plan: step-by-step plan
- train_entrypoint: path to training script
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from state import ReplicatorState
from llm.client import build_llm
from llm.prompts import ANALYZE_REPO_SYSTEM, ANALYZE_REPO_USER


def analyze_code(state: ReplicatorState, config: dict) -> dict:
    llm = build_llm(config["configurable"]["replicator_config"])

    prompt = ANALYZE_REPO_USER.format(
        repo_url=state["repo_url"],
        readme=state["readme"] or "(no README found)",
        file_tree=state["file_tree"],
        requirements=state["requirements"] or "(no requirements file found)",
    )

    response = llm.invoke([
        SystemMessage(content=ANALYZE_REPO_SYSTEM),
        HumanMessage(content=prompt),
    ])

    try:
        # Strip markdown code fences if present
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(text)
    except (json.JSONDecodeError, IndexError) as e:
        return {"error": f"LLM returned invalid JSON: {e}", "phase": "analyze"}

    return {
        "introduction": data.get("introduction", ""),
        "preview": data.get("preview", {}),
        "reproduction_plan": data.get("reproduction_plan", []),
        "train_entrypoint": data.get("train_entrypoint", ""),
        "code_summary": json.dumps(data, ensure_ascii=False, indent=2),
        "error": "",
        "phase": "analyze_code",
    }
