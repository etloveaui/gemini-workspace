import argparse
import sys
from pathlib import Path
import difflib

# 프로젝트 루트 디렉토리를 sys.path에 추가하고, rules 모듈을 임포트합니다.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.agents.rules import get_rule, get_rule_names, load_rules

def _assert_within_project_boundary(file_path: Path):
    """파일 경로가 프로젝트 작업 공간 내에 있는지 확인합니다."""
    resolved_path = file_path.resolve()
    if not resolved_path.is_relative_to(ROOT.resolve()):
        print(f"Error: Path '{resolved_path}' is outside the allowed project boundary '{ROOT.resolve()}'.", file=sys.stderr)
        sys.exit(4) # 표준 Exit Code: 일반 오류

def main():
    # argparse를 사용하여 CLI 인자를 파싱합니다.
    # --yes와 --apply를 모두 --apply로 처리하고, --list와 --explain을 추가합니다.
    parser = argparse.ArgumentParser(description="Refactor files based on a plugin-driven rule system.")
    parser.add_argument("--file", help="The file to refactor.")
    parser.add_argument("--rule", help="The refactoring rule to apply.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them.")
    parser.add_argument("--yes", "--apply", dest="apply", action="store_true", help="Apply changes without confirmation.")
    parser.add_argument("--list", action="store_true", help="List all available refactoring rules.")
    parser.add_argument("--explain", metavar="RULE_NAME", help="Explain a specific refactoring rule.")
    
    # 규칙별 추가 인자를 받을 수 있도록 parse_known_args를 사용합니다.
    args, unknown_args = parser.parse_known_args()

    # 1. 규칙 목록 또는 설명 요청 처리
    load_rules() # 모든 규칙을 동적으로 로드
    if args.list:
        print("Available refactoring rules:")
        for name in get_rule_names():
            print(f"- {name}")
        sys.exit(0)

    if args.explain:
        try:
            rule_cls = get_rule(args.explain)
            print(f"Rule: {rule_cls.name}")
            print(f"Summary: {rule_cls.summary}")
            if rule_cls.params:
                print("Parameters:")
                for param, desc in rule_cls.params.items():
                    print(f"  --{param}: {desc}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(4)
        sys.exit(0)

    # 2. 리팩토링 실행을 위한 필수 인자 검증
    if not args.file or not args.rule:
        parser.print_help()
        sys.exit(1)

    # 3. 파일 경로 검증 및 보안 검사
    file_path = ROOT / args.file
    _assert_within_project_boundary(file_path)
    if not file_path.is_file():
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

    # 4. 규칙 실행 및 diff 생성
    try:
        rule_cls = get_rule(args.rule)
        # 규칙별 추가 인자를 파싱하여 kwargs로 전달합니다.
        rule_kwargs = {k.lstrip('-'): v for k, v in zip(unknown_args[::2], unknown_args[1::2])}
        rule_instance = rule_cls()
        
        source_code = file_path.read_text(encoding='utf-8')
        new_code = rule_instance.apply(source_code, **rule_kwargs)

    except (ValueError, TypeError) as e:
        print(f"Error executing rule '{args.rule}': {e}", file=sys.stderr)
        sys.exit(4)

    diff = difflib.unified_diff(
        source_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile=f"a/{args.file}",
        tofile=f"b/{args.file}",
    )
    diff_output = "".join(diff)

    if not diff_output:
        print("No changes to apply.")
        sys.exit(0)

    # 5. 결과 출력 및 실제 적용
    print("The following changes are proposed:")
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console()
    syntax = Syntax(diff_output, "diff", theme="monokai", line_numbers=True)
    console.print(syntax)

    if args.dry_run:
        print("\nDry run mode. No changes were applied.")
        sys.exit(0)

    if not args.apply:
        # 대화형 확인이 필요한 경우 (runner.py의 confirm_action은 invoke 태스크 레벨에서 사용)
        # 여기서는 간단한 input으로 대체하거나, --yes 플래그를 강제하도록 유도합니다.
        try:
            confirm = input("\nApply these changes? [y/N] ")
            if confirm.lower() != 'y':
                print("Refactoring cancelled.")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("\nRefactoring cancelled.")
            sys.exit(1)

    # 6. 백업 및 파일 쓰기 (안전장치)
    try:
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        file_path.rename(backup_path)
        file_path.write_text(new_code, encoding='utf-8')
        backup_path.unlink() # 성공 시 백업 파일 삭제
        print(f"\nSuccessfully refactored '{args.file}'.")
    except Exception as e:
        print(f"Error applying changes: {e}. Original file restored from .bak", file=sys.stderr)
        # 실패 시 원상 복구 시도
        if backup_path.exists():
            backup_path.rename(file_path)
        sys.exit(1)

if __name__ == "__main__":
    main()