"""
report.py — progressive markdown report for each task.
Updated after each pipeline phase; stored at <workspace>/<task_name>/report.md
"""

from datetime import datetime
from pathlib import Path


def _report_path(workspace: str, task_name: str) -> Path:
    p = Path(workspace).expanduser() / task_name
    p.mkdir(parents=True, exist_ok=True)
    return p / "report.md"


def init_report(workspace: str, task_name: str, repo_url: str):
    """Create a fresh report file with header."""
    path = _report_path(workspace, task_name)
    content = f"""# Replicator Report: {task_name}

**Repo:** {repo_url}
**Started:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---
"""
    path.write_text(content, encoding="utf-8")


def update_report(workspace: str, task_name: str, section: str, content: str):
    """Append or replace a section in the report.

    Sections are delimited by `## <section>` headers.
    If the section already exists it is replaced; otherwise appended.
    """
    path = _report_path(workspace, task_name)
    if not path.exists():
        return

    current = path.read_text(encoding="utf-8")
    new_section = f"## {section}\n\n{content.strip()}\n"

    marker = f"## {section}"
    if marker in current:
        # Replace existing section up to the next ## or end of file
        lines = current.split("\n")
        out, inside = [], False
        for line in lines:
            if line.startswith(marker):
                inside = True
                out.append(new_section)
                continue
            if inside and line.startswith("## "):
                inside = False
            if not inside:
                out.append(line)
        path.write_text("\n".join(out), encoding="utf-8")
    else:
        path.write_text(current.rstrip() + "\n\n" + new_section, encoding="utf-8")
