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

    # -- Phase 1a: Clone & read --
    repo_local_path: str         # local clone path
    readme: str
    requirements: str
    file_tree: str               # filtered file tree

    # -- Phase 1b: Key file identification --
    key_files: list              # LLM-selected important files
    file_contents: dict          # {path: content} of key files

    # -- Phase 1c: Deep analysis --
    introduction: str            # LLM: what this project is
    file_breakdown: list         # LLM: per-file explanation
    preview: dict                # LLM: architecture overview
    reproduction_plan: list      # LLM: step-by-step plan
    train_entrypoint: str        # e.g. "train.py"
    code_summary: str            # full LLM JSON output

    # -- Phase 2: Environment setup --
    env_setup_log: str
    env_ready: bool
    env_activate_prefix: str     # e.g. "conda run -n myenv" or ""

    # -- Phase 3: Quick run --
    quick_run_cmd: str           # command planned by LLM
    required_inputs: list        # [{name, description, env_var, required}]
    user_inputs: dict            # {ENV_VAR: value} collected from user
    quick_run_log: str           # combined stdout/stderr
    quick_run_success: bool      # True if first step confirmed
    diagnosis: str               # LLM error analysis (if failed)

    # -- Phase 4+: Experiment loop (future) --
    experiments: Annotated[list[Experiment], operator.add]
    current_experiment_id: int
    heartbeat_count: int
    iteration: int
    max_iterations: int

    # -- Control --
    error: str
    phase: str
