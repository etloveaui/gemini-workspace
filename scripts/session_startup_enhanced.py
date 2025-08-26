#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Claude Code 세션 시작 자동화 스크립트 v2.0
- 기존 기능 + 자동 모니터링 + 스마트 업데이트 통합
- 완전 자동화된 시작 프로세스
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime
import json

# 환경 경로 관리 시스템 사용
from environment_path_manager import get_workspace_path
try:
    from usage_logging import record_event
except Exception:
    def record_event(*args, **kwargs):
        pass
from claude_comm_cleaner import clean_all_communications

def session_startup_complete():
    """완전한 세션 시작 프로세스"""
    print("🚀 Claude Code 세션 시작 자동화 v2.0")
    try:
        record_event(task_name="session_startup_enhanced", event_type="start", command="session_startup_complete")
    except Exception:
        pass
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 환경 정보 및 현재 위치 출력
    from environment_path_manager import path_manager
    workspace_root = get_workspace_path()
    env_info = path_manager.get_environment_info()
    
    print(f"📁 현재 위치: {workspace_root}")
    print(f"👤 사용자: {env_info['user']}")
    print(f"💻 호스트: {env_info['hostname']}")
    print(f"🔧 플랫폼: {env_info['platform']}")
    print(f"🆔 환경 ID: {env_info['environment_id']}")
    
    # 새로운 환경 감지 및 프로필 생성
    if not env_info['profile_loaded']:
        print(f"🔄 새로운 환경 감지! 프로필 생성 중...")
        path_manager.create_environment_profile()
        print(f"✅ 환경 프로필 생성 완료")
    
    # 2. Communication 폴더 자동 정리
    print("\n📋 Communication 폴더 자동 정리...")
    try:
        total_cleaned = clean_all_communications()
        if total_cleaned > 0:
            print(f"✅ {total_cleaned}개 파일이 archive로 정리됨")
        else:
            print("✅ 정리할 파일 없음")
    except Exception as e:
        print(f"❌ Comm 정리 오류: {e}")
    
    # 3. 필수 파일 확인
    print("\n📄 필수 파일 확인...")
    file_status = verify_critical_files()
    for file_path, exists in file_status.items():
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
    
    # 4. 자동 모니터링 실행
    print("\n🔍 자동 모니터링 시스템 시작...")
    monitoring_results = run_auto_monitoring()
    
    if isinstance(monitoring_results, dict) and "error" not in monitoring_results:
        changes = monitoring_results.get("changes", {})
        health = monitoring_results.get("health", {})
        
        print(f"📊 새 파일: {len(changes.get('new_files', []))}개, 수정: {len(changes.get('modified_files', []))}개")
        print(f"💊 시스템 상태: {health.get('overall_status', 'unknown')}")
        
        # 중요한 변경사항 알림
        if changes.get("integration_suggestions"):
            print("🚀 통합 제안 있음!")
            for suggestion in changes["integration_suggestions"][:3]:  # 최대 3개만 표시
                print(f"  • {suggestion.get('suggestion', 'Unknown')}")
    else:
        print(f"⚠️ 모니터링: {monitoring_results.get('error', '실행 안됨')}")
    
    # 5. 스마트 업데이트 확인
    print("\n🔄 스마트 업데이트 확인...")
    update_results = run_smart_updates()
    
    if isinstance(update_results, dict) and "error" not in update_results:
        new_mcp = len(update_results.get("new_mcp_servers", []))
        new_agents = len(update_results.get("new_agents", []))
        new_scripts = len(update_results.get("new_scripts", []))
        
        if new_mcp + new_agents + new_scripts > 0:
            print(f"🔗 자동 통합: MCP {new_mcp}개, 에이전트 {new_agents}개, 스크립트 {new_scripts}개")
        else:
            print("✅ 새로운 통합 대상 없음")
    else:
        print(f"⚠️ 업데이트: {update_results.get('error', '실행 안됨')}")
    
    # 6. MCP 시스템 상태 확인
    print("\n🔌 MCP 시스템 상태...")
    try:
        from mcp_auto_system import get_workspace_status_auto, health_check_auto
        mcp_status = get_workspace_status_auto()
        mcp_health = health_check_auto()
        
        print(f"✅ MCP 사용 가능: {mcp_status.get('mcp_available', False)}")
        print(f"💊 MCP 상태: {mcp_health.get('status', 'unknown')}")
    except Exception as e:
        print(f"⚠️ MCP 상태 확인 실패: {e}")
    
    # 7. 에이전트 활동 상태
    print("\n🤖 에이전트 활동 상태...")
    try:
        from mcp_auto_system import mcp_auto
        activities = mcp_auto.get_agent_activities()
        
        for agent, activity in activities.items():
            if isinstance(activity, list) and activity:
                print(f"✅ {agent.upper()}: 최근 활동 {len(activity)}건")
            else:
                print(f"💤 {agent.upper()}: 활동 없음")
    except Exception as e:
        print(f"⚠️ 에이전트 활동 확인 실패: {e}")
    
    # 8. 사용자 주의사항
    print("\n" + "=" * 60)
    print("🎯 세션 준비 완료! 주요 확인사항:")
    print("📋 HUB_ENHANCED.md - 현재 작업 상황 확인")
    print("🔍 자동 모니터링 - 새로운 변경사항 추적")
    print("🤖 MCP 시스템 - 토큰 효율적 사용")
    print("⚡ 다음 명령어로 추가 확인:")
    print("   - from session_startup_enhanced import *")
    print("   - run_full_status_check()")
    print("=" * 60)
    
    result = {
        "status": "complete",
        "timestamp": datetime.now().isoformat(),
        "files_checked": len(file_status),
        "monitoring_active": "error" not in monitoring_results,
        "updates_checked": "error" not in update_results
    }
    try:
        record_event(task_name="session_startup_enhanced", event_type="complete", command="session_startup_complete")
    except Exception:
        pass
    return result

def verify_critical_files() -> dict:
    """중요 파일들 존재 확인"""
    critical_files = [
        "CLAUDE.md",
        "docs/CORE/AGENTS_CHECKLIST.md", 
        "docs/CORE/HUB_ENHANCED.md",
        "scripts/mcp_auto_system.py",
        "scripts/agent_task_dispatcher.py",
        "scripts/auto_monitoring_system.py",
        "scripts/smart_update_system.py"
    ]
    
    status = {}
    for file_path in critical_files:
        full_path = get_workspace_path(file_path)
        status[file_path] = full_path.exists()
    
    return status

def run_auto_monitoring():
    """자동 모니터링 실행"""
    try:
        from auto_monitoring_system import run_full_monitoring
        return run_full_monitoring()
    except ImportError as e:
        return {"error": f"모니터링 모듈 로드 실패: {e}"}
    except Exception as e:
        return {"error": f"모니터링 실행 실패: {e}"}

def run_smart_updates():
    """스마트 업데이트 실행"""
    try:
        from smart_update_system import run_auto_update
        return run_auto_update()
    except ImportError as e:
        return {"error": f"업데이트 모듈 로드 실패: {e}"}
    except Exception as e:
        return {"error": f"업데이트 실행 실패: {e}"}

def run_full_status_check():
    """전체 상태 종합 확인"""
    print("🔍 워크스페이스 종합 상태 확인")
    print("=" * 50)
    
    # 파일 상태
    file_status = verify_critical_files()
    missing_files = [f for f, exists in file_status.items() if not exists]
    
    if missing_files:
        print(f"❌ 누락 파일: {len(missing_files)}개")
        for file in missing_files[:3]:  # 최대 3개만 표시
            print(f"   • {file}")
    else:
        print("✅ 모든 중요 파일 존재")
    
    # 모니터링 상태
    monitoring = run_auto_monitoring()
    if "error" not in monitoring:
        print("✅ 자동 모니터링 정상")
    else:
        print(f"❌ 모니터링: {monitoring['error']}")
    
    # 업데이트 상태
    updates = run_smart_updates()
    if "error" not in updates:
        print("✅ 스마트 업데이트 정상")
    else:
        print(f"❌ 업데이트: {updates['error']}")
    
    # MCP 상태
    try:
        from mcp_auto_system import mcp_auto
        print(f"✅ MCP 시스템: {'정상' if mcp_auto.mcp_available else '제한적'}")
    except:
        print("❌ MCP 시스템 확인 불가")
    
    print("=" * 50)

# 편의 함수들 (직접 호출 가능)
def comm_cleanup_quick():
    """빠른 통신 정리 (Claude 전용)"""
    from claude_comm_cleaner import clean_agent_communication
    clean_agent_communication("claude")

def verify_files_quick():
    """빠른 파일 확인"""
    return verify_critical_files()

def startup_all():
    """전체 시작 프로세스"""
    return session_startup_complete()

if __name__ == "__main__":
    result = session_startup_complete()
    print(f"\n📊 결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
