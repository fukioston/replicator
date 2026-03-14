from typing import TypedDict, Annotated, Literal
import operator


class Experiment(TypedDict):
    id: int
    config: dict
    job_id: str
    status: Literal["pending", "running", "done", "failed"]
    results: dict
    notes: str


class ReplicatorState(TypedDict):
    # -- Input --
    repo_url: str
    workspace_dir: str           # local workspace root (~/replicator-workspace)
    ssh_host: str
    ssh_user: str
    ssh_key_path: str
    remote_workdir: str          # remote experiment dir (SSH mode)

    # -- Phase 1: Repo analysis --
    repo_local_path: str         # local clone path
    readme: str
    requirements: str
    file_tree: str
    introduction: str            # LLM: what this project is
    preview: dict                # LLM: key files and architecture
    reproduction_plan: list      # LLM: step-by-step plan
    train_entrypoint: str        # e.g. "train.py"
    code_summary: str            # full LLM JSON output

    # -- Phase 2: Environment --
    env_setup_log: str
    env_ready: bool

    # -- Phase 3+: Experiment loop --
    experiments: Annotated[list[Experiment], operator.add]
    current_experiment_id: int
    heartbeat_count: int
    iteration: int
    max_iterations: int

    # -- Control --
    error: str
    phase: str
