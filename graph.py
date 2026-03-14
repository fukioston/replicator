import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path

from state import ReplicatorState
from nodes.clone_and_read import clone_and_read
from nodes.identify_key_files import identify_key_files
from nodes.analyze_code import analyze_code
from nodes.setup_env import setup_env
from nodes.plan_quick_run import plan_quick_run
from nodes.gather_user_inputs import gather_user_inputs
from nodes.execute_quick_run import execute_quick_run
from nodes.diagnose_error import diagnose_error


# -- Routing --

def _has_error(state: ReplicatorState) -> bool:
    return bool(state.get("error"))


def route_after_clone(state: ReplicatorState) -> str:
    return "handle_error" if _has_error(state) else "identify_key_files"


def route_after_analyze(state: ReplicatorState) -> str:
    return "handle_error" if _has_error(state) else "setup_env"


def route_after_setup(state: ReplicatorState) -> str:
    return "handle_error" if _has_error(state) else "plan_quick_run"


def route_after_plan(state: ReplicatorState) -> str:
    return "handle_error" if _has_error(state) else "gather_user_inputs"


def route_after_execute(state: ReplicatorState) -> str:
    if state.get("quick_run_success"):
        return END
    return "diagnose_error"


def handle_error(state: ReplicatorState) -> dict:
    print(f"\n[ERROR] Phase: {state.get('phase')} — {state.get('error')}")
    return {}


# -- Graph --

def clear_checkpoint(workspace_dir: str, thread_id: str):
    """Delete all checkpoint data for a given thread_id."""
    db_path = str(Path(workspace_dir).expanduser() / "replicator.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for table in ("checkpoints", "checkpoint_blobs", "checkpoint_writes"):
        try:
            cur.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))
        except sqlite3.OperationalError:
            pass  # table may not exist yet
    conn.commit()
    conn.close()


def build_graph(workspace_dir: str):
    db_path = str(Path(workspace_dir).expanduser() / "replicator.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    g = StateGraph(ReplicatorState)

    g.add_node("clone_and_read", clone_and_read)
    g.add_node("identify_key_files", identify_key_files)
    g.add_node("analyze_code", analyze_code)
    g.add_node("setup_env", setup_env)
    g.add_node("plan_quick_run", plan_quick_run)
    g.add_node("gather_user_inputs", gather_user_inputs)
    g.add_node("execute_quick_run", execute_quick_run)
    g.add_node("diagnose_error", diagnose_error)
    g.add_node("handle_error", handle_error)

    g.set_entry_point("clone_and_read")
    g.add_conditional_edges("clone_and_read", route_after_clone)
    g.add_edge("identify_key_files", "analyze_code")
    g.add_conditional_edges("analyze_code", route_after_analyze)
    g.add_conditional_edges("setup_env", route_after_setup)
    g.add_conditional_edges("plan_quick_run", route_after_plan)
    g.add_edge("gather_user_inputs", "execute_quick_run")
    g.add_conditional_edges("execute_quick_run", route_after_execute)
    g.add_edge("diagnose_error", END)
    g.add_edge("handle_error", END)

    return g.compile(checkpointer=checkpointer)
