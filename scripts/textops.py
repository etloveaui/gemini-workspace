from __future__ import annotations

import argparse
from pathlib import Path


def detect_line_ending_bytes(data: bytes) -> str:
    """Return 'crlf', 'lf', or 'mixed' based on byte content."""
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n")
    # lf counts all newlines including CRLF; adjust pure LF count
    pure_lf = lf - crlf
    if crlf and pure_lf:
        return 'mixed'
    if crlf:
        return 'crlf'
    return 'lf'


def normalize_to_lf(text: str) -> str:
    return text.replace('\r\n', '\n').replace('\r', '\n')


def render_with_style(text_lf: str, style: str) -> str:
    if style == 'crlf':
        return text_lf.replace('\n', '\r\n')
    return text_lf


def replace_with_lineending_tolerance(path: Path, old: str, new: str, expect: int = 0, dry_run: bool = False) -> int:
    data = path.read_bytes() if path.exists() else b""
    style = detect_line_ending_bytes(data)
    content = data.decode('utf-8', errors='replace')
    content_lf = normalize_to_lf(content)
    old_lf = normalize_to_lf(old)
    new_lf = normalize_to_lf(new)
    count = content_lf.count(old_lf)
    if expect and count != expect:
        raise ValueError(f"expected {expect} replacements, found {count}")
    if count == 0:
        return 0
    updated_lf = content_lf.replace(old_lf, new_lf)
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_with_style(updated_lf, style), encoding='utf-8')
    return count


def cmd_replace(args):
    path = Path(args.file)
    try:
        n = replace_with_lineending_tolerance(path, args.old, args.new, expect=args.expect, dry_run=args.dry_run)
        if args.dry_run:
            print(f"dry-run: would replace {n} occurrence(s)")
        else:
            print(f"replaced {n} occurrence(s)")
    except Exception as e:
        print(f"error: {e}")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser("text operations")
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('replace')
    p.add_argument('--file', required=True)
    p.add_argument('--old', required=True)
    p.add_argument('--new', required=True)
    p.add_argument('--expect', type=int, default=0)
    p.add_argument('--dry-run', action='store_true')
    p.set_defaults(func=cmd_replace)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

