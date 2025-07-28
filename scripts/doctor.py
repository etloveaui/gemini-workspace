#!/usr/bin/env python
import shutil, sys, os
from pathlib import Path
from importlib import util

sys.stdout.reconfigure(encoding='utf-8')

REPORT = []

def check(name, ok, hint=""):
    status = "[PASS]" if ok else "[FAIL]"
    REPORT.append((status, name, hint))

def main():
    # Python
    py_ok = sys.version_info >= (3, 10)
    check("Python >= 3.10", py_ok, "Python 3.10 이상을 설치하세요.")

    # Invoke
    invoke_ok = shutil.which("invoke") is not None
    check("Invoke installed", invoke_ok, "pip install invoke")

    # Git
    git_ok = shutil.which("git") is not None
    check("Git installed", git_ok, "https://git-scm.com/")

    # venv
    venv_ok = sys.prefix != sys.base_prefix
    check("Virtualenv active", venv_ok, "venv를 활성화하세요. source venv/bin/activate")

    # files
    root = Path(__file__).parent.parent
    usage_ok = (root / "usage.db").exists()
    check("usage.db exists", usage_ok, "invoke start 또는 log 발생 후 자동 생성됩니다.")
    no_delete_ok = (root / ".no_delete_list").exists()
    check(".no_delete_list exists", no_delete_ok, "루트에 .no_delete_list 생성하세요.")
    gemini_ok = (root / "GEMINI.md").exists()
    check("GEMINI.md exists", gemini_ok, "GEMINI.md가 삭제되었는지 확인하세요.")

    # Summary
    fails = [r for r in REPORT if r[0] == "[FAIL]"]
    for status, name, hint in REPORT:
        line = f"{status} {name}"
        if status == "[FAIL]":
            line += f" -> {hint}"
        print(line)

    print("\n---")
    if fails:
        print(f"{len(fails)}개의 문제가 발견되었습니다. 위의 해결 팁을 참고하세요.")
        sys.exit(1)
    else:
        print("모든 시스템 점검 완료. 문제 없음.")
        sys.exit(0)

if __name__ == "__main__":
    main()

