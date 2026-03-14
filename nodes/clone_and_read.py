"""
clone_and_read: Clone the repo locally and read key files.
No LLM call — pure I/O.
"""

import os
import subprocess
from pathlib import Path

from rich.console import Console
from state import ReplicatorState

console = Console()


def clone_and_read(state: ReplicatorState) -> dict:
    repo_url = state["repo_url"]
    workspace = Path(state["workspace_dir"]).expanduser()
    repo_name = repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
    local_path = workspace / "repos" / repo_name

    # Clone (skip if already exists)
    if not local_path.exists():
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with console.status(f"[cyan]Cloning {repo_url}...[/cyan]"):
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(local_path)],
                capture_output=True, text=True,
            )
        if result.returncode != 0:
            return {"error": f"git clone failed: {result.stderr}", "phase": "clone"}
    else:
        console.print(f"[dim]Already cloned, using existing: {local_path}[/dim]")

    # Read README
    readme = ""
    for name in ["README.md", "README.rst", "README.txt", "README"]:
        p = local_path / name
        if p.exists():
            readme = p.read_text(errors="ignore")[:8000]
            break

    # Read requirements
    requirements = ""
    for name in ["requirements.txt", "pyproject.toml", "setup.py", "environment.yml"]:
        p = local_path / name
        if p.exists():
            requirements = p.read_text(errors="ignore")[:3000]
            break

    # Build file tree (2 levels deep)
    file_tree = _build_tree(local_path, max_depth=2)

    return {
        "repo_local_path": str(local_path),
        "readme": readme,
        "requirements": requirements,
        "file_tree": file_tree,
        "error": "",
        "phase": "clone_and_read",
    }


def _build_tree(root: Path, max_depth: int) -> str:
    lines = []
    _walk(root, root, 0, max_depth, lines)
    return "\n".join(lines)


def _walk(root: Path, current: Path, depth: int, max_depth: int, lines: list):
    if depth > max_depth:
        return
    indent = "  " * depth
    skip = {".git", "__pycache__", ".venv", "node_modules", ".eggs"}
    try:
        entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return
    for entry in entries:
        if entry.name in skip:
            continue
        lines.append(f"{indent}{'📁 ' if entry.is_dir() else ''}{entry.name}")
        if entry.is_dir():
            _walk(root, entry, depth + 1, max_depth, lines)
