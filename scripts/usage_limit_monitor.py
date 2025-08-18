#!/usr/bin/env python3
"""
Claude 사용량 제한 모니터링 시스템
- 토큰 사용량 추적 및 제한 임박 시 경고
- API 호출 빈도 모니터링
- 사용량 패턴 분석 및 최적화 제안
"""

import os
import sys
import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class UsageLimitMonitor:
    """사용량 제한 모니터링 시스템"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.usage_db_path = self.workspace_path / "usage.db"
        self.usage_log_path = self.workspace_path / "logs" / "usage_monitor.log"
        
        # Claude 사용량 제한 (추정치)
        self.limits = {
            "messages_per_hour": 50,
            "tokens_per_hour": 200000,
            "messages_per_day": 500,
            "tokens_per_day": 2000000,
            "reset_time_seoul": 16  # 오후 4시 (Asia/Seoul)
        }
        
        # 경고 임계값 (사용량 %로 설정)
        self.warning_thresholds = {
            "yellow": 70,  # 70% 사용 시 주의
            "orange": 85,  # 85% 사용 시 경고
            "red": 95      # 95% 사용 시 위험
        }
        
        self.current_usage = {
            "messages_hour": 0,
            "tokens_hour": 0,
            "messages_day": 0,
            "tokens_day": 0,
            "last_reset": datetime.now()
        }
        
        self._ensure_directories()
        self._initialize_database()
    
    def _ensure_directories(self):
        """필요한 디렉터리 생성"""
        self.usage_log_path.parent.mkdir(exist_ok=True)
    
    def _initialize_database(self):
        """사용량 추적 데이터베이스 초기화"""
        if not self.usage_db_path.exists():
            return
        
        try:
            conn = sqlite3.connect(self.usage_db_path)
            cursor = conn.cursor()
            
            # 사용량 모니터링 테이블 생성 (이미 있다면 무시)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_monitor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tool_name TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    execution_time REAL DEFAULT 0,
                    context_size INTEGER DEFAULT 0,
                    success BOOLEAN DEFAULT TRUE,
                    warning_level TEXT DEFAULT 'green'
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            self._log(f"데이터베이스 초기화 오류: {e}")
    
    def _log(self, message: str, level: str = "INFO"):
        """사용량 모니터 전용 로깅"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        try:
            with open(self.usage_log_path, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"로그 기록 실패: {e}")
    
    def record_usage(self, tool_name: str, tokens_used: int = 0, 
                    execution_time: float = 0, context_size: int = 0, 
                    success: bool = True):
        """도구 사용량 기록"""
        try:
            # 현재 사용량 업데이트
            self.current_usage["messages_hour"] += 1
            self.current_usage["tokens_hour"] += tokens_used
            self.current_usage["messages_day"] += 1
            self.current_usage["tokens_day"] += tokens_used
            
            # 경고 레벨 계산
            warning_level = self._calculate_warning_level()
            
            # 데이터베이스에 기록
            if self.usage_db_path.exists():
                conn = sqlite3.connect(self.usage_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO usage_monitor 
                    (tool_name, tokens_used, execution_time, context_size, success, warning_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tool_name, tokens_used, execution_time, context_size, success, warning_level))
                
                conn.commit()
                conn.close()
            
            # 경고 확인 및 알림
            self._check_and_warn(warning_level)
            
        except Exception as e:
            self._log(f"사용량 기록 오류: {e}", "ERROR")
    
    def _calculate_warning_level(self) -> str:
        """현재 사용량 기준 경고 레벨 계산"""
        # 시간당 및 일일 사용량 비율 계산
        hour_msg_pct = (self.current_usage["messages_hour"] / self.limits["messages_per_hour"]) * 100
        hour_token_pct = (self.current_usage["tokens_hour"] / self.limits["tokens_per_hour"]) * 100
        day_msg_pct = (self.current_usage["messages_day"] / self.limits["messages_per_day"]) * 100
        day_token_pct = (self.current_usage["tokens_day"] / self.limits["tokens_per_day"]) * 100
        
        # 가장 높은 사용률 기준으로 경고 레벨 결정
        max_usage = max(hour_msg_pct, hour_token_pct, day_msg_pct, day_token_pct)
        
        if max_usage >= self.warning_thresholds["red"]:
            return "red"
        elif max_usage >= self.warning_thresholds["orange"]:
            return "orange"
        elif max_usage >= self.warning_thresholds["yellow"]:
            return "yellow"
        else:
            return "green"
    
    def _check_and_warn(self, warning_level: str):
        """경고 레벨에 따른 알림 처리"""
        if warning_level == "red":
            self._log("위험: 사용량 한도 95% 초과! 즉시 사용을 중단하세요!", "CRITICAL")
            print("\n" + "="*60)
            print("🚨 CRITICAL: Claude 사용량 한도 95% 초과!")
            print("즉시 사용을 중단하고 한도 리셋을 기다리세요.")
            print(f"다음 리셋 시간: 오후 {self.limits['reset_time_seoul']}시 (Asia/Seoul)")
            print("="*60 + "\n")
            
        elif warning_level == "orange":
            self._log("경고: 사용량 한도 85% 초과. 주의가 필요합니다.", "WARNING")
            print("\n" + "-"*50)
            print("⚠️  WARNING: Claude 사용량 한도 85% 초과")
            print("사용량을 줄이거나 작업을 나누어 진행하세요.")
            print("-"*50 + "\n")
            
        elif warning_level == "yellow":
            self._log("주의: 사용량 한도 70% 도달. 사용량을 모니터링하세요.", "INFO")
            print("💡 INFO: Claude 사용량 70% 도달. 사용량 주의하세요.")
    
    def get_current_status(self) -> Dict:
        """현재 사용량 상태 반환"""
        return {
            "current_usage": self.current_usage.copy(),
            "limits": self.limits.copy(),
            "warning_level": self._calculate_warning_level(),
            "percentages": {
                "messages_hour": (self.current_usage["messages_hour"] / self.limits["messages_per_hour"]) * 100,
                "tokens_hour": (self.current_usage["tokens_hour"] / self.limits["tokens_per_hour"]) * 100,
                "messages_day": (self.current_usage["messages_day"] / self.limits["messages_per_day"]) * 100,
                "tokens_day": (self.current_usage["tokens_day"] / self.limits["tokens_per_day"]) * 100
            }
        }
    
    def reset_counters_if_needed(self):
        """필요시 카운터 리셋 (시간/일일 기준)"""
        now = datetime.now()
        last_reset = self.current_usage["last_reset"]
        
        # 일일 리셋 확인 (오후 4시 기준)
        reset_time_today = now.replace(hour=self.limits["reset_time_seoul"], minute=0, second=0, microsecond=0)
        if now.hour >= self.limits["reset_time_seoul"] and last_reset < reset_time_today:
            self._log("일일 사용량 카운터 리셋")
            self.current_usage["messages_day"] = 0
            self.current_usage["tokens_day"] = 0
            self.current_usage["last_reset"] = now
        
        # 시간별 리셋 확인
        if (now - last_reset).total_seconds() >= 3600:  # 1시간
            self._log("시간별 사용량 카운터 리셋")
            self.current_usage["messages_hour"] = 0
            self.current_usage["tokens_hour"] = 0
            self.current_usage["last_reset"] = now
    
    def generate_usage_report(self, days: int = 7) -> str:
        """사용량 분석 보고서 생성"""
        if not self.usage_db_path.exists():
            return "사용량 데이터가 없습니다."
        
        try:
            conn = sqlite3.connect(self.usage_db_path)
            cursor = conn.cursor()
            
            # 최근 N일간 데이터 조회
            since_date = datetime.now() - timedelta(days=days)
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as total_calls,
                    SUM(tokens_used) as total_tokens,
                    AVG(execution_time) as avg_time,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failures,
                    COUNT(CASE WHEN warning_level != 'green' THEN 1 END) as warnings
                FROM usage_monitor 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (since_date.isoformat(),))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return "최근 사용량 데이터가 없습니다."
            
            # 보고서 생성
            report = f"# Claude 사용량 분석 보고서 (최근 {days}일)\n\n"
            report += f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            report += "## 📊 일별 사용량 통계\n\n"
            report += "| 날짜 | 호출수 | 토큰수 | 평균시간 | 실패 | 경고 |\n"
            report += "|------|--------|--------|----------|------|------|\n"
            
            total_calls = 0
            total_tokens = 0
            total_failures = 0
            total_warnings = 0
            
            for row in results:
                date, calls, tokens, avg_time, failures, warnings = row
                report += f"| {date} | {calls} | {tokens:,} | {avg_time:.2f}s | {failures} | {warnings} |\n"
                
                total_calls += calls
                total_tokens += tokens or 0
                total_failures += failures or 0
                total_warnings += warnings or 0
            
            report += f"\n**합계**: 호출 {total_calls}회, 토큰 {total_tokens:,}개, 실패 {total_failures}회, 경고 {total_warnings}회\n\n"
            
            # 현재 상태
            status = self.get_current_status()
            report += "## 🔄 현재 상태\n\n"
            report += f"- **시간당 메시지**: {status['current_usage']['messages_hour']}/{status['limits']['messages_per_hour']} ({status['percentages']['messages_hour']:.1f}%)\n"
            report += f"- **시간당 토큰**: {status['current_usage']['tokens_hour']:,}/{status['limits']['tokens_per_hour']:,} ({status['percentages']['tokens_hour']:.1f}%)\n"
            report += f"- **일일 메시지**: {status['current_usage']['messages_day']}/{status['limits']['messages_per_day']} ({status['percentages']['messages_day']:.1f}%)\n"
            report += f"- **일일 토큰**: {status['current_usage']['tokens_day']:,}/{status['limits']['tokens_per_day']:,} ({status['percentages']['tokens_day']:.1f}%)\n"
            report += f"- **현재 경고 레벨**: {status['warning_level'].upper()}\n\n"
            
            # 최적화 제안
            report += "## 💡 사용량 최적화 제안\n\n"
            
            if status['warning_level'] in ['orange', 'red']:
                report += "### ⚠️ 즉시 조치 필요\n"
                report += "- 큰 작업을 여러 세션으로 나누어 진행\n"
                report += "- 불필요한 파일 재읽기 방지\n"
                report += "- 컨텍스트 크기 최적화\n\n"
            
            report += "### 일반적인 최적화 방법\n"
            report += "- **새 대화 세션 시작**: 긴 대화는 컨텍스트 크기가 증가합니다\n"
            report += "- **여러 질문 통합**: 하나의 메시지에 여러 질문을 포함하세요\n"
            report += "- **Projects 기능 활용**: 문서를 캐시하여 토큰 사용량 절약\n"
            report += f"- **피크 시간 회피**: 오전 9시-오후 6시 (미국 동부) 시간대 피하기\n\n"
            
            return report
            
        except Exception as e:
            return f"보고서 생성 오류: {e}"
    
    def estimate_tokens(self, text: str) -> int:
        """텍스트의 대략적인 토큰 수 추정"""
        # 간단한 추정: 영어 기준 4자당 1토큰, 한글 기준 2자당 1토큰
        english_chars = sum(1 for c in text if ord(c) < 128)
        korean_chars = len(text) - english_chars
        
        return (english_chars // 4) + (korean_chars // 2)
    
    def check_conversation_length_warning(self, conversation_text: str) -> Tuple[bool, str]:
        """대화창 길이 기준 제한 임박 경고"""
        estimated_tokens = self.estimate_tokens(conversation_text)
        
        # Claude의 컨텍스트 윈도우 기준 (대략 200k 토큰)
        context_limit = 200000
        warning_thresholds = {
            "yellow": int(context_limit * 0.6),   # 60% - 120k 토큰
            "orange": int(context_limit * 0.8),   # 80% - 160k 토큰  
            "red": int(context_limit * 0.9)       # 90% - 180k 토큰
        }
        
        if estimated_tokens >= warning_thresholds["red"]:
            return True, f"[CRITICAL] 대화 길이 90% 초과 ({estimated_tokens:,}/{context_limit:,} 토큰). 새 대화 시작 권장!"
        elif estimated_tokens >= warning_thresholds["orange"]:
            return True, f"[WARNING] 대화 길이 80% 도달 ({estimated_tokens:,}/{context_limit:,} 토큰). 곧 새 대화가 필요합니다."
        elif estimated_tokens >= warning_thresholds["yellow"]:
            return True, f"[INFO] 대화 길이 60% 도달 ({estimated_tokens:,}/{context_limit:,} 토큰). 대화 길이를 주의하세요."
        
        return False, f"대화 길이 정상 ({estimated_tokens:,}/{context_limit:,} 토큰)"

def main():
    """사용량 모니터 메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude 사용량 모니터링")
    parser.add_argument("--status", action="store_true", help="현재 상태 확인")
    parser.add_argument("--report", type=int, metavar="DAYS", default=7, 
                       help="사용량 보고서 생성 (기본: 7일)")
    parser.add_argument("--record", nargs=3, metavar=("TOOL", "TOKENS", "TIME"),
                       help="사용량 기록 (도구명 토큰수 실행시간)")
    
    args = parser.parse_args()
    
    monitor = UsageLimitMonitor()
    
    if args.status:
        status = monitor.get_current_status()
        print("\n📊 Claude 사용량 현재 상태")
        print("="*40)
        print(f"시간당 메시지: {status['current_usage']['messages_hour']}/{status['limits']['messages_per_hour']} ({status['percentages']['messages_hour']:.1f}%)")
        print(f"시간당 토큰:   {status['current_usage']['tokens_hour']:,}/{status['limits']['tokens_per_hour']:,} ({status['percentages']['tokens_hour']:.1f}%)")
        print(f"일일 메시지:   {status['current_usage']['messages_day']}/{status['limits']['messages_per_day']} ({status['percentages']['messages_day']:.1f}%)")
        print(f"일일 토큰:     {status['current_usage']['tokens_day']:,}/{status['limits']['tokens_per_day']:,} ({status['percentages']['tokens_day']:.1f}%)")
        print(f"경고 레벨:     {status['warning_level'].upper()}")
        print("="*40)
    
    elif args.record:
        tool_name, tokens_str, time_str = args.record
        try:
            tokens = int(tokens_str)
            exec_time = float(time_str)
            monitor.record_usage(tool_name, tokens, exec_time)
            print(f"사용량 기록 완료: {tool_name} ({tokens} 토큰, {exec_time}초)")
        except ValueError:
            print("오류: 토큰수와 실행시간은 숫자여야 합니다.")
    
    else:
        # 기본: 보고서 생성
        report = monitor.generate_usage_report(args.report)
        print(report)
        
        # 파일로도 저장
        report_file = monitor.workspace_path / "docs" / "usage_report.md"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 보고서 저장됨: {report_file}")

if __name__ == "__main__":
    main()