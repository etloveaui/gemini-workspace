import argparse
import sys
from pathlib import Path
import ast
import difflib

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def add_docstrings(source_code):
    tree = ast.parse(source_code)
    new_tree = tree
    for node in ast.walk(new_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)):
                docstring = ast.Expr(value=ast.Str(s='"""TODO: Add docstring."""'))
                node.body.insert(0, docstring)
    return ast.unparse(new_tree)

def main():
    parser = argparse.ArgumentParser(description="Refactor files based on rules.")
    parser.add_argument("--file", required=True, help="The file to refactor.")
    parser.add_argument("--rule", required=True, help="The refactoring rule to apply.")
    parser.add_argument("--dry-run", action="store_true", help="If set, shows the changes without applying them.")
    args = parser.parse_args()

    file_path = ROOT / args.file
    if not file_path.is_file():
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    source_code = file_path.read_text(encoding='utf-8')

    if args.rule == "add_docstrings":
        new_code = add_docstrings(source_code)
    else:
        print(f"Error: Unknown rule '{args.rule}'")
        sys.exit(1)

    if args.dry_run:
        diff = difflib.unified_diff(
            source_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile=f"a/{args.file}",
            tofile=f"b/{args.file}",
        )
        sys.stdout.writelines(diff)
    else:
        file_path.write_text(new_code, encoding='utf-8')
        print(f"Successfully refactored {args.file}")

if __name__ == "__main__":
    main()
