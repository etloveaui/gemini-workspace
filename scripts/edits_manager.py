from __future__ import annotations

import argparse
from pathlib import Path
import os
import sys
import difflib

ROOT = Path(__file__).resolve().parents[1]
EDITS = ROOT / ".edits" / "proposals"


def _target_path(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if not str(p).startswith(str(ROOT)):
        raise ValueError("Path must be inside repo")
    return p


def _proposal_path(rel: str) -> Path:
    return EDITS / rel


def cmd_capture(args):
    rel = args.file.replace("\\", "/").lstrip("/")
    src = _target_path(rel)
    dst = _proposal_path(rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        dst.write_text("", encoding="utf-8")
    else:
        dst.write_text(src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(str(dst))


def cmd_propose(args):
    rel = args.file.replace("\\", "/").lstrip("/")
    dst = _proposal_path(rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if args.from_file:
        content = Path(args.from_file).read_text(encoding="utf-8", errors="replace")
    else:
        content = args.content or ""
    dst.write_text(content, encoding="utf-8")
    print(str(dst))


def _diff_one(rel: str) -> str:
    src_path = _target_path(rel)
    prop_path = _proposal_path(rel)
    src = src_path.read_text(encoding="utf-8", errors="replace").splitlines(True) if src_path.exists() else []
    dst = prop_path.read_text(encoding="utf-8", errors="replace").splitlines(True) if prop_path.exists() else []
    return "".join(difflib.unified_diff(src, dst, fromfile=str(src_path), tofile=str(src_path)+" (proposed)", lineterm=""))


def cmd_list(args):
    for p in EDITS.rglob("*"):
        if p.is_file():
            print(p.relative_to(EDITS).as_posix())


def cmd_diff(args):
    if args.file:
        rel = args.file.replace("\\", "/").lstrip("/")
        print(_diff_one(rel))
    else:
        for p in sorted(EDITS.rglob("*")):
            if p.is_file():
                rel = p.relative_to(EDITS).as_posix()
                print(_diff_one(rel))


def cmd_apply(args):
    rel = args.file.replace("\\", "/").lstrip("/") if args.file else None
    targets = [rel] if rel else [p.relative_to(EDITS).as_posix() for p in EDITS.rglob("*") if p.is_file()]
    if not targets:
        print("no proposals")
        return
    auto_yes = os.getenv("EDITS_AUTO_YES") in {"1", "true", "True"}
    for t in targets:
        diff = _diff_one(t)
        if not diff.strip():
            continue
        print(diff)
        ok = auto_yes
        if not ok:
            try:
                ans = input(f"Apply above change for {t}? [y/N]: ").strip().lower()
                ok = ans in {"y", "yes"}
            except EOFError:
                ok = False
        if not ok:
            continue
        # write proposed to target
        src_path = _target_path(t)
        prop_path = _proposal_path(t)
        src_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.write_text(prop_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        # optional: delete proposal
        if not args.keep:
            try:
                prop_path.unlink()
            except OSError:
                pass
    print("done")


def cmd_discard(args):
    rel = args.file.replace("\\", "/").lstrip("/")
    p = _proposal_path(rel)
    if p.exists():
        p.unlink()
        print("discarded")
    else:
        print("not_found")


def main():
    parser = argparse.ArgumentParser("edits manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cap = sub.add_parser("capture")
    p_cap.add_argument("--file", required=True)
    p_cap.set_defaults(func=cmd_capture)

    p_prop = sub.add_parser("propose")
    p_prop.add_argument("--file", required=True)
    p_prop.add_argument("--from-file")
    p_prop.add_argument("--content")
    p_prop.set_defaults(func=cmd_propose)

    p_ls = sub.add_parser("list")
    p_ls.set_defaults(func=cmd_list)

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("--file")
    p_diff.set_defaults(func=cmd_diff)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--file")
    p_apply.add_argument("--keep", action="store_true")
    p_apply.set_defaults(func=cmd_apply)

    p_dis = sub.add_parser("discard")
    p_dis.add_argument("--file", required=True)
    p_dis.set_defaults(func=cmd_discard)

    args = parser.parse_args()
    EDITS.mkdir(parents=True, exist_ok=True)
    args.func(args)


if __name__ == "__main__":
    main()

