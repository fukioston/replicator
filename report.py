"""
report.py — progressive markdown report for each task.
Updated after each pipeline phase; stored at <workspace>/<task_name>/report.md
"""

from datetime import datetime
from pathlib import Path

_LABELS = {
    "中文": {
        "title":              "复现报告",
        "repo":               "仓库",
        "started":            "开始时间",
        "Introduction":       "项目介绍",
        "File Breakdown":     "文件说明",
        "Reproduction Plan":  "复现计划",
        "Quick Run":          "快速验证",
        "Error Diagnosis":    "错误诊断",
        "Error":              "错误",
    },
    "日本語": {
        "title":              "再現レポート",
        "repo":               "リポジトリ",
        "started":            "開始日時",
        "Introduction":       "プロジェクト概要",
        "File Breakdown":     "ファイル説明",
        "Reproduction Plan":  "再現手順",
        "Quick Run":          "動作確認",
        "Error Diagnosis":    "エラー診断",
        "Error":              "エラー",
    },
}

def _l(lang: str, key: str) -> str:
    return _LABELS.get(lang, {}).get(key, key)


def _report_path(workspace: str, task_name: str) -> Path:
    p = Path(workspace).expanduser() / task_name
    p.mkdir(parents=True, exist_ok=True)
    return p / "report.md"


def init_report(workspace: str, task_name: str, repo_url: str, lang: str = "English"):
    """Create a fresh report file with header."""
    path = _report_path(workspace, task_name)
    content = f"""# {_l(lang, 'title')}: {task_name}

**{_l(lang, 'repo')}:** {repo_url}
**{_l(lang, 'started')}:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---
"""
    path.write_text(content, encoding="utf-8")


def update_report(workspace: str, task_name: str, section: str, content: str, lang: str = "English"):
    """Append or replace a section in the report.

    Sections are delimited by `## <section>` headers.
    If the section already exists it is replaced; otherwise appended.
    """
    path = _report_path(workspace, task_name)
    if not path.exists():
        return

    current = path.read_text(encoding="utf-8")
    translated = _l(lang, section)
    new_section = f"## {translated}\n\n{content.strip()}\n"

    marker = f"## {translated}"
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
