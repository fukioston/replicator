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
    ssh_host: str
    ssh_user: str
    ssh_key_path: str
    remote_workdir: str          # e.g. ~/replicator-workspace/<repo-name>

    # -- Phase 1: Repo analysis --
    repo_local_path: str         # local clone path (under ~/replicator-workspace)
    readme: str
    requirements: str
    file_tree: str
    train_entrypoint: str        # e.g. "train.py"
    code_summary: str

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
