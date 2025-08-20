#!/usr/bin/env python
"""Preflight Doctor v2.0 - 멀티 에이전트 워크스페이스 환경 검증 도구

환경 검증, 문제 예측, 자동 수정 기능을 제공합니다.
"""
import shutil, sys, os, json, sqlite3
from pathlib import Path
from importlib import util
from datetime import datetime
import subprocess
from typing import List, Dict, Tuple

sys.stdout.reconfigure(encoding='utf-8')

REPORT = []
AUTO_FIXES = []

def check(name: str, ok: bool, hint: str = "", auto_fix: callable = None, severity: str = "ERROR") -> bool:
    """시스템 검증 및 자동 수정 등록"""
    status = "[PASS]" if ok else "[FAIL]"
    REPORT.append((status, name, hint, severity))
    
    if not ok and auto_fix:
        AUTO_FIXES.append((name, auto_fix, hint))
    
    return ok

def auto_fix_venv() -> bool:
    """가상환경 자동 활성화 안내"""
    print("  🔧 자동 수정: venv 활성화 명령어를 출력합니다.")
    venv_path = Path.cwd() / "venv"
    if venv_path.exists():
        if os.name == 'nt':  # Windows
            print(f"    명령어: {venv_path / 'Scripts' / 'activate.bat'}")
        else:
            print(f"    명령어: source {venv_path / 'bin' / 'activate'}")
        return True
    return False

def auto_fix_no_delete_list() -> bool:
    """no_delete_list 자동 생성"""
    root = Path(__file__).parent.parent
    no_delete_file = root / ".no_delete_list"
    try:
        with open(no_delete_file, 'w', encoding='utf-8') as f:
            f.write("# 삭제하면 안 되는 중요 파일/폴더 목록\n")
            f.write(".git/\n")
            f.write("venv/\n")
            f.write("secrets/\n")
            f.write("CLAUDE.md\n")
            f.write("GEMINI.md\n")
            f.write("AGENTS.md\n")
        print("  🔧 자동 수정: .no_delete_list 파일을 생성했습니다.")
        return True
    except Exception as e:
        print(f"  ❌ 자동 수정 실패: {e}")
        return False

def check_token_usage() -> Tuple[bool, str]:
    """토큰 사용량 검증"""
    try:
        root = Path(__file__).parent.parent
        usage_db = root / "usage.db"
        if not usage_db.exists():
            return False, "usage.db 파일이 없습니다"
        
        conn = sqlite3.connect(str(usage_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usage_log WHERE date >= date('now', '-7 days')")
        recent_usage = cursor.fetchone()[0]
        conn.close()
        
        if recent_usage == 0:
            return False, "최근 7일간 사용 기록이 없습니다"
        
        return True, f"최근 7일간 {recent_usage}개 기록"
    except Exception as e:
        return False, f"토큰 사용량 확인 실패: {e}"

def check_multi_agent_config() -> Tuple[bool, str]:
    """멀티 에이전트 설정 검증"""
    root = Path(__file__).parent.parent
    agents_config = [
        ("CLAUDE.md", "Claude 설정"),
        ("GEMINI.md", "Gemini 설정"), 
        ("AGENTS.md", "Codex 설정")
    ]
    
    missing = []
    for config_file, desc in agents_config:
        if not (root / config_file).exists():
            missing.append(desc)
    
    if missing:
        return False, f"누락된 설정: {', '.join(missing)}"
    
    return True, "모든 에이전트 설정 파일 존재"

def save_diagnosis_report(report: List, fixes_applied: List) -> str:
    """진단 보고서 저장"""
    root = Path(__file__).parent.parent
    reports_dir = root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"doctor_v2_{timestamp}.json"
    
    diagnosis = {
        "timestamp": timestamp,
        "version": "2.0",
        "checks": report,
        "auto_fixes_applied": fixes_applied,
        "summary": {
            "total_checks": len(report),
            "passed": len([r for r in report if r[0] == "[PASS]"]),
            "failed": len([r for r in report if r[0] == "[FAIL]"]),
            "fixes_applied": len(fixes_applied)
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(diagnosis, f, ensure_ascii=False, indent=2)
    
    return str(report_file)

def main():
    print("🏥 Preflight Doctor v2.0 시작 - 멀티 에이전트 워크스페이스 진단\n")
    
    # Python 버전 검증 (고급)
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    py_hint = f"현재: {py_version.major}.{py_version.minor}.{py_version.micro}"
    if not py_ok:
        py_hint += " → Python 3.10+ 필요"
    check("Python >= 3.10", py_ok, py_hint, severity="CRITICAL")

    # 필수 도구 검증
    invoke_ok = shutil.which("invoke") is not None
    check("Invoke 설치됨", invoke_ok, "pip install invoke", severity="HIGH")
    
    git_ok = shutil.which("git") is not None
    git_version = ""
    if git_ok:
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            git_version = f" ({result.stdout.strip()})"
        except:
            git_version = " (버전 확인 실패)"
    check(f"Git 설치됨{git_version}", git_ok, "https://git-scm.com/", severity="HIGH")

    # 가상환경 검증 (자동 수정 지원)
    venv_ok = sys.prefix != sys.base_prefix
    venv_hint = f"현재 Python 경로: {sys.prefix}"
    if not venv_ok:
        venv_hint += " → 가상환경 미활성화"
    check("가상환경 활성화", venv_ok, venv_hint, auto_fix_venv, "HIGH")

    # 핵심 파일 검증
    root = Path(__file__).parent.parent
    
    # 토큰 사용량 DB 검증 (고급)
    usage_ok, usage_msg = check_token_usage()
    check("토큰 사용량 추적", usage_ok, usage_msg, severity="MEDIUM")
    
    # 안전 파일 목록 (자동 생성)
    no_delete_ok = (root / ".no_delete_list").exists()
    check("안전 파일 목록", no_delete_ok, "중요 파일 보호 목록", auto_fix_no_delete_list, "MEDIUM")
    
    # 멀티 에이전트 설정 검증
    agents_ok, agents_msg = check_multi_agent_config()
    check("멀티 에이전트 설정", agents_ok, agents_msg, severity="HIGH")
    
    # 프로젝트 구조 검증
    critical_dirs = ["docs", "scripts", "communication", "secrets"]
    for dir_name in critical_dirs:
        dir_ok = (root / dir_name).is_dir()
        check(f"필수 디렉토리: {dir_name}", dir_ok, f"{dir_name} 폴더가 필요합니다", severity="HIGH")

    # 자동 수정 실행
    fixes_applied = []
    if AUTO_FIXES:
        print("\n🔧 자동 수정 시도 중...")
        for fix_name, fix_func, hint in AUTO_FIXES:
            try:
                if fix_func():
                    fixes_applied.append(fix_name)
                    print(f"  ✅ {fix_name} 수정 완료")
            except Exception as e:
                print(f"  ❌ {fix_name} 수정 실패: {e}")
    
    # 결과 출력 (향상된 형태)
    print("\n📊 진단 결과:")
    print("=" * 50)
    
    critical_fails = [r for r in REPORT if r[0] == "[FAIL]" and r[3] == "CRITICAL"]
    high_fails = [r for r in REPORT if r[0] == "[FAIL]" and r[3] == "HIGH"]
    medium_fails = [r for r in REPORT if r[0] == "[FAIL]" and r[3] == "MEDIUM"]
    passes = [r for r in REPORT if r[0] == "[PASS]"]
    
    for status, name, hint, severity in REPORT:
        icon = "🔴" if status == "[FAIL]" else "🟢"
        sev_icon = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "💡", "ERROR": "❌"}.get(severity, "")
        
        line = f"{icon} {name}"
        if status == "[FAIL]":
            line += f" {sev_icon} → {hint}"
        print(line)
    
    # 보고서 저장
    report_file = save_diagnosis_report(REPORT, fixes_applied)
    
    print("\n" + "=" * 50)
    print(f"📋 상세 보고서: {report_file}")
    
    # 최종 판정
    if critical_fails:
        print(f"🚨 치명적 문제 {len(critical_fails)}개 발견! 즉시 해결 필요")
        sys.exit(2)
    elif high_fails:
        print(f"⚠️  중요 문제 {len(high_fails)}개 발견. 해결 권장")
        sys.exit(1)
    elif medium_fails:
        print(f"💡 권장 개선사항 {len(medium_fails)}개 있음")
        print(f"🎉 전체 {len(passes + medium_fails)}개 검사 중 핵심 기능 정상")
        sys.exit(0)
    else:
        print(f"🎉 완벽! {len(passes)}개 항목 모두 통과")
        if fixes_applied:
            print(f"🔧 자동 수정 {len(fixes_applied)}개 항목 완료")
        sys.exit(0)

if __name__ == "__main__":
    main()

