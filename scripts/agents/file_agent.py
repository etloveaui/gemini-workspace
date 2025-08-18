#!/usr/bin/env python3
"""
더미 파일 에이전트 - 테스트용
"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="File Agent (Test Dummy)")
    parser.add_argument('--list', action='store_true', help="List available rules")
    parser.add_argument('--explain', help="Explain a rule")
    parser.add_argument('--file', help="Target file")
    parser.add_argument('--rule', help="Rule to apply")
    parser.add_argument('--dry-run', action='store_true', help="Dry run mode")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available refactoring rules:")
        print("- add_docstrings")
        print("- format_code")
        return 0
    
    if args.explain:
        if args.explain == "add_docstrings":
            print("Rule: add_docstrings")
            print("Summary:")
            print("Adds docstrings to functions")
        else:
            print(f"Unknown rule: '{args.explain}'")
        return 0
    
    if args.rule:
        if args.rule not in ["add_docstrings", "format_code"]:
            print(f"Unknown rule: '{args.rule}'", file=sys.stderr)
            return 1
        
        if args.file:
            mode = "dry-run" if args.dry_run else "apply"
            print(f"[{mode}] Applying rule '{args.rule}' to '{args.file}'")
            return 0
    
    print("File agent ready")
    return 0

if __name__ == "__main__":
    sys.exit(main())