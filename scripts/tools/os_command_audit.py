from __future__ import annotations

import ast
import re
from pathlib import Path
import argparse
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]


RISKY_TOKENS = [
    # Common POSIX-only commands often mistakenly used on Windows
    r"\brm\b",
    r"\bmv\b",
    r"\bcp\b",
    r"\bln\b",
]


def iter_files(base: Path) -> Iterable[Path]:
    for p in base.rglob("*"):
        if p.is_dir():
            continue
        if any(str(p).startswith(str(ROOT / d)) for d in [
            ".git", "venv", "secrets", "projects", "logs", "__pycache__",
        ]):
            continue
        if p.suffix.lower() in {".py", ".ps1", ".cmd", ".bat"}:
            yield p


def audit_text_file(path: Path) -> list[str]:
    out: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return out
    for i, line in enumerate(text.splitlines(), 1):
        for pat in RISKY_TOKENS:
            if re.search(pat, line):
                out.append(f"{path}:{i}: {line.strip()}")
                break
    return out


def audit_python_subprocess(path: Path) -> list[str]:
    out: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = getattr(getattr(node.func, "attr", None), "lower", lambda: "")()
            qual = None
            if isinstance(node.func, ast.Attribute):
                qual = getattr(getattr(node.func, "value", None), "id", None)
            if func_name in {"run", "popen"} and qual == "subprocess":
                shell_kw = next((kw for kw in node.keywords if kw.arg == "shell"), None)
                if shell_kw and getattr(shell_kw.value, "value", False):
                    out.append(f"{path}: subprocess.{func_name}(shell=True) may be OS fragile")
    return out


def main() -> int:
    ap = argparse.ArgumentParser("OS command consistency audit")
    ap.add_argument("--target", default=str(ROOT), help="Target directory to scan (default: repo root)")
    ap.add_argument("--out", default=str(ROOT / "logs" / "os_command_audit.txt"), help="Report output path")
    ap.add_argument("--max", dest="max_items", type=int, default=2000, help="Max items to report")
    args = ap.parse_args()

    base = Path(args.target).resolve()
    out_path = Path(args.out).resolve()

    issues: list[str] = []
    count = 0
    for p in iter_files(base):
        # Only scan shell-like files for risky POSIX tokens to reduce false positives
        if p.suffix.lower() in {".ps1", ".cmd", ".bat", ".sh"}:
            issues.extend(audit_text_file(p))
        # For Python, use AST heuristics only
        if p.suffix.lower() == ".py":
            issues.extend(audit_python_subprocess(p))
        if len(issues) > args.max_items:
            break

    report_path = out_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    # Summary header
    header = [
        f"Target: {base}",
        f"Total issues: {len(issues)}",
        "",
    ]
    report_path.write_text("\n".join(header + issues[: args.max_items]), encoding="utf-8")
    print(f"Found {len(issues)} potential issues. Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
