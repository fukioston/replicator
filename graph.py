import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path

from state import ReplicatorState
from nodes.clone_and_read import clone_and_read
from nodes.identify_key_files import identify_key_files
from nodes.analyze_code import analyze_code


# -- Routing --

def route_after_clone(state: ReplicatorState) -> str:
    return "handle_error" if state.get("error") else "identify_key_files"


def route_after_analyze(state: ReplicatorState) -> str:
    return "handle_error" if state.get("error") else END


def handle_error(state: ReplicatorState) -> dict:
    print(f"\n[ERROR] Phase: {state.get('phase')} — {state.get('error')}")
    return {}


# -- Graph --

def build_graph(workspace_dir: str):
    db_path = str(Path(workspace_dir).expanduser() / "replicator.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    g = StateGraph(ReplicatorState)

    g.add_node("clone_and_read", clone_and_read)
    g.add_node("identify_key_files", identify_key_files)
    g.add_node("analyze_code", analyze_code)
    g.add_node("handle_error", handle_error)

    g.set_entry_point("clone_and_read")
    g.add_conditional_edges("clone_and_read", route_after_clone)
    g.add_edge("identify_key_files", "analyze_code")
    g.add_conditional_edges("analyze_code", route_after_analyze)
    g.add_edge("handle_error", END)

    return g.compile(checkpointer=checkpointer)
