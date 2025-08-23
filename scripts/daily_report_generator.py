#!/usr/bin/env python3
"""
일일 보고서 자동 생성 및 상태 관리 시스템
- past day 날짜 자동 변경 문제 해결
- 보고서 완료 상태 자동 추적 문제 해결
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
COMM_PATH = ROOT / "communication"
TEMPLATES_PATH = COMM_PATH / "templates"
STATUS_FILE = ROOT / "docs/CORE/daily_status.json"

def generate_daily_file(agent="claude", days_ago=0):
    """
    일일 작업 파일을 자동 생성하고 날짜를 올바르게 설정
    
    Args:
        agent: 에이전트 이름 (claude, gemini, codex)
        days_ago: 며칠 전 날짜로 설정할지 (0=오늘, 1=어제)
    """
    target_date = datetime.now() - timedelta(days=days_ago)
    date_str = target_date.strftime("%Y%m%d")
    formatted_date = target_date.strftime("%Y-%m-%d")
    
    # 템플릿 읽기
    template_file = TEMPLATES_PATH / "daily_template.md"
    if not template_file.exists():
        print(f"[ERROR] 템플릿 파일이 없습니다: {template_file}")
        return None
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 날짜와 시간 자동 치환
    current_time = datetime.now().strftime("%H:%M")
    content = template_content.replace("YYYY-MM-DD", formatted_date)
    content = content.replace("HH:MM", current_time)
    content = content.replace("agent: claude|gemini|codex", f"agent: {agent}")
    
    # 파일 생성
    agent_comm_path = COMM_PATH / agent
    agent_comm_path.mkdir(exist_ok=True)
    
    output_file = agent_comm_path / f"{date_str}_01_daily_work.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] 일일 작업 파일 생성: {output_file}")
    return output_file

def check_report_status():
    """
    현재 진행 중인 보고서들의 완료 상태를 체크하고 요약
    """
    print("[CHECK] 보고서 상태 체크 중...")
    
    status_data = {
        "last_check": datetime.now().isoformat(),
        "reports": {}
    }
    
    # proposals 폴더의 보고서들 체크
    proposals_path = ROOT / "docs" / "proposals"
    if proposals_path.exists():
        for file in proposals_path.glob("*.md"):
            if "report" in file.name.lower():
                # 파일 수정 시간으로 완료 여부 추정
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                is_recent = (datetime.now() - mod_time).days < 7
                
                status_data["reports"][file.name] = {
                    "path": str(file),
                    "modified": mod_time.isoformat(),
                    "status": "completed" if is_recent else "old",
                    "size": file.stat().st_size
                }
    
    # 상태 파일 저장
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)
    
    # 결과 출력
    print(f"[UPDATE] 보고서 상태 업데이트: {STATUS_FILE}")
    
    completed_reports = [name for name, data in status_data["reports"].items() 
                        if data["status"] == "completed"]
    old_reports = [name for name, data in status_data["reports"].items() 
                  if data["status"] == "old"]
    
    if completed_reports:
        print("[COMPLETE] 최근 완료된 보고서들:")
        for report in completed_reports:
            print(f"  - {report}")
    
    if old_reports:
        print("[ARCHIVE] 오래된 보고서들 (아카이브 필요):")
        for report in old_reports:
            print(f"  - {report}")
    
    return status_data

def fix_past_day_issues():
    """
    "past day 바꾼거?" 문제를 영구적으로 해결
    기존 템플릿의 날짜 형식을 자동화된 형식으로 변경
    """
    print("[FIX] Past Day 문제 해결 중...")
    
    # 어제 날짜로 파일 생성
    yesterday_file = generate_daily_file("claude", days_ago=1)
    
    # 오늘 날짜로 파일 생성
    today_file = generate_daily_file("claude", days_ago=0)
    
    # 다른 에이전트들도 동일하게 생성
    gemini_today = generate_daily_file("gemini", days_ago=0)
    codex_today = generate_daily_file("codex", days_ago=0)
    
    print("[OK] Past Day 문제 해결 완료!")
    print("[OK] 모든 에이전트용 daily_work.md 생성 완료!")
    return [yesterday_file, today_file, gemini_today, codex_today]

def main():
    """메인 실행 함수"""
    print("== 일일 보고서 자동 생성 시스템 ==")
    print("=" * 50)
    
    # 1. Past Day 문제 해결
    generated_files = fix_past_day_issues()
    
    print("\n" + "=" * 50)
    
    # 2. 보고서 상태 체크
    report_status = check_report_status()
    
    print("\n" + "=" * 50)
    print("시스템 업데이트 완료!")
    print("\n해결된 문제들:")
    print("  1. Past Day 날짜 자동 생성")
    print("  2. 보고서 완료 상태 자동 추적")
    print("  3. 일일 작업 파일 자동화")
    
    print(f"\n상태 파일 위치: {STATUS_FILE}")
    print(f"생성된 파일: {len(generated_files)}개")

if __name__ == "__main__":
    main()