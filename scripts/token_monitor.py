"""
토큰 사용량 실시간 모니터링 시스템
- Codex, Gemini, Claude 토큰 사용량 추적
- 한도 초과 방지 알림 시스템
"""
import argparse
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line, divider


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "usage.db"

# 추정 토큰 한도 (실제 API 제한과 다를 수 있음)
TOKEN_LIMITS = {
    'codex': 25000000,  # OpenAI Codex 추정치
    'gemini': 1048576,  # Google Gemini 1.0 Pro
    'claude': 200000,   # Anthropic Claude (컨텍스트 윈도우)
}

def check_token_usage(agent_name=None):
    """토큰 사용량 확인"""
    print(header("토큰 사용량 현황"))
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        if agent_name:
            # 특정 에이전트 사용량
            cursor.execute("""
                SELECT COUNT(*) as total_tasks,
                       SUM(LENGTH(stdout) + LENGTH(stderr) + LENGTH(command)) as estimated_tokens
                FROM usage_log 
                WHERE task_name LIKE ? OR command LIKE ?
            """, (f"%{agent_name}%", f"%{agent_name}%"))
            
            result = cursor.fetchone()
            total_tasks, estimated_tokens = result
            estimated_tokens = estimated_tokens or 0
            
            limit = TOKEN_LIMITS.get(agent_name.lower(), 1000000)
            usage_percent = (estimated_tokens / limit) * 100
            
            print(kv("에이전트", agent_name.upper()))
            print(kv("총 작업 수", total_tasks))
            print(kv("추정 토큰", f"{estimated_tokens:,}"))
            print(kv("토큰 한도", f"{limit:,}"))
            print(kv("사용률", f"{usage_percent:.1f}%"))
            
            # 경고 시스템
            if usage_percent > 80:
                print(status_line(1, "CRITICAL", "토큰 한도", "80% 초과 - 즉시 작업 중단 필요"))
            elif usage_percent > 60:
                print(status_line(2, "WARNING", "토큰 한도", "60% 초과 - 주의 필요"))
            else:
                print(status_line(3, "OK", "토큰 한도", "안전 범위"))
                
        else:
            # 전체 에이전트 요약
            for agent in TOKEN_LIMITS.keys():
                cursor.execute("""
                    SELECT COUNT(*) as total_tasks,
                           SUM(LENGTH(stdout) + LENGTH(stderr) + LENGTH(command)) as estimated_tokens
                    FROM usage_log 
                    WHERE task_name LIKE ? OR command LIKE ?
                """, (f"%{agent}%", f"%{agent}%"))
                
                result = cursor.fetchone()
                total_tasks, estimated_tokens = result
                estimated_tokens = estimated_tokens or 0
                
                limit = TOKEN_LIMITS[agent]
                usage_percent = (estimated_tokens / limit) * 100
                
                status = "OK" if usage_percent < 60 else "WARNING" if usage_percent < 80 else "CRITICAL"
                print(status_line(list(TOKEN_LIMITS.keys()).index(agent) + 1, status, 
                                agent.upper(), f"{usage_percent:.1f}% ({estimated_tokens:,}/{limit:,})"))


def reset_token_counter(agent_name):
    """토큰 카운터 리셋 (주의해서 사용)"""
    print(header("토큰 카운터 리셋"))
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usage_log WHERE task_name LIKE ? OR command LIKE ?", 
                      (f"%{agent_name}%", f"%{agent_name}%"))
        deleted_count = cursor.rowcount
        conn.commit()
        
    print(kv("리셋 완료", f"{agent_name} - {deleted_count}개 레코드 삭제"))


def main():
    parser = argparse.ArgumentParser(description='토큰 사용량 모니터링')
    parser.add_argument('--agent', help='특정 에이전트 확인 (codex/gemini/claude)')
    parser.add_argument('--check-usage', action='store_true', help='토큰 사용량 확인')
    parser.add_argument('--reset', help='특정 에이전트 토큰 카운터 리셋')
    
    args = parser.parse_args()
    
    if args.check_usage:
        check_token_usage(args.agent)
    elif args.reset:
        reset_token_counter(args.reset)
    else:
        check_token_usage()


if __name__ == "__main__":
    main()