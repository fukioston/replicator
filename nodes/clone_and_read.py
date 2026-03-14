"""
clone_and_read: Clone the repo locally and read key files.
No LLM call — pure I/O.

File tree strategy:
- Skip noise dirs (tests, docs, data, __pycache__, etc.)
- Only keep relevant extensions (.py, .yaml, .sh, .toml, etc.)
- If file count > FILE_THRESHOLD, switch to directory-level summary
"""

import subprocess
from pathlib import Path
from rich.console import Console

from state import ReplicatorState

console = Console()

# Dirs to always skip
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env", "node_modules",
    ".eggs", "dist", "build", "wandb", ".mypy_cache", ".pytest_cache",
    "tests", "test", "docs", "doc", "data", "dataset", "datasets",
    "outputs", "output", "logs", "log", "checkpoints", "checkpoint",
    "samples", "assets", "images", "figures", "paper",
}

# Extensions worth showing
KEEP_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".sh", ".toml", ".cfg",
    ".json", ".md", ".txt", ".ipynb",
}

# Switch to directory summary if more than this many files
FILE_THRESHOLD = 150


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
        console.print(f"[dim]Already cloned → {local_path}[/dim]")

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

    # Build filtered file tree
    file_tree, file_count = _build_filtered_tree(local_path)

    if file_count > FILE_THRESHOLD:
        console.print(
            f"[yellow]⚠ Large repo ({file_count} files), using directory-level summary[/yellow]"
        )

    return {
        "repo_local_path": str(local_path),
        "readme": readme,
        "requirements": requirements,
        "file_tree": file_tree,
        "key_files": [],
        "file_contents": {},
        "error": "",
        "phase": "clone_and_read",
    }


def _build_filtered_tree(root: Path) -> tuple[str, int]:
    """Returns (tree_string, total_file_count)."""
    all_files = _collect_files(root)
    total = len(all_files)

    if total > FILE_THRESHOLD:
        return _directory_summary(root), total
    else:
        return _file_listing(root, all_files), total


def _collect_files(root: Path) -> list[Path]:
    """Collect all relevant files, skipping noise."""
    result = []
    for p in root.rglob("*"):
        if p.is_file():
            # Skip if any parent dir is in SKIP_DIRS
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix in KEEP_EXTENSIONS or p.name in {"Makefile", "Dockerfile"}:
                result.append(p.relative_to(root))
    return sorted(result)


def _file_listing(root: Path, files: list[Path]) -> str:
    """Standard file tree for small repos."""
    lines = []
    seen_dirs = set()
    for f in files:
        for i, part in enumerate(f.parts[:-1]):
            dir_key = f.parts[:i+1]
            if dir_key not in seen_dirs:
                seen_dirs.add(dir_key)
                lines.append("  " * i + f"📁 {part}/")
        lines.append("  " * (len(f.parts) - 1) + f.name)
    return "\n".join(lines)


def _directory_summary(root: Path) -> str:
    """Directory-level summary for large repos."""
    lines = ["(Large repo — directory summary)"]
    for entry in sorted(root.iterdir()):
        if entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if entry.is_dir():
            py_files = list(entry.rglob("*.py"))
            total_files = list(entry.rglob("*"))
            exts = {f.suffix for f in total_files if f.is_file() and f.suffix}
            lines.append(
                f"📁 {entry.name}/  ({len(py_files)} .py, {len(total_files)} total files, "
                f"exts: {', '.join(sorted(exts)[:5])})"
            )
        else:
            if entry.suffix in KEEP_EXTENSIONS or entry.name in {"Makefile", "Dockerfile"}:
                lines.append(f"  {entry.name}")
    return "\n".join(lines)
