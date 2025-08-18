#!/usr/bin/env python3
"""
Claude Code 토큰 사용량 모니터링 시스템
- 실시간 토큰 사용량 추적
- 한도 근접 시 자동 알림
- 작업 중단 방지 메커니즘
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

class TokenMonitor:
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.log_file = self.workspace_path / "logs" / "token_usage.jsonl"
        self.config_file = self.workspace_path / ".claude" / "token_config.json"
        self.warning_file = self.workspace_path / "TOKEN_WARNING.md"
        
        # 기본 설정
        self.default_config = {
            "daily_limit": 100000,  # 일일 토큰 한도
            "warning_threshold": 0.8,  # 80% 도달 시 경고
            "critical_threshold": 0.95,  # 95% 도달 시 위험
            "session_limit": 50000,  # 세션당 권장 한도
            "monitoring_enabled": True
        }
        
        self.ensure_directories()
        self.load_config()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        self.log_file.parent.mkdir(exist_ok=True)
        self.config_file.parent.mkdir(exist_ok=True)
    
    def load_config(self):
        """설정 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = {**self.default_config, **json.load(f)}
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        """설정 저장"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def log_usage(self, tokens_used, context="unknown", session_id=None):
        """토큰 사용량 로깅"""
        if not self.config["monitoring_enabled"]:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tokens_used": tokens_used,
            "context": context,
            "session_id": session_id or self.get_session_id(),
            "daily_total": self.get_daily_total() + tokens_used
        }
        
        # JSONL 형식으로 로그 기록
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # 경고 체크
        self.check_limits(entry["daily_total"], tokens_used)
    
    def get_session_id(self):
        """현재 세션 ID 생성"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_daily_total(self):
        """오늘 사용한 총 토큰 수 계산"""
        if not self.log_file.exists():
            return 0
        
        today = datetime.now().date()
        total = 0
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_date = datetime.fromisoformat(entry["timestamp"]).date()
                    if entry_date == today:
                        total += entry["tokens_used"]
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return total
    
    def get_session_total(self, session_id=None):
        """현재 세션 토큰 사용량"""
        if not self.log_file.exists():
            return 0
        
        if session_id is None:
            session_id = self.get_session_id()
        
        total = 0
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("session_id") == session_id:
                        total += entry["tokens_used"]
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return total
    
    def check_limits(self, daily_total, current_usage):
        """한도 체크 및 경고 생성"""
        daily_limit = self.config["daily_limit"]
        warning_threshold = self.config["warning_threshold"]
        critical_threshold = self.config["critical_threshold"]
        
        usage_ratio = daily_total / daily_limit
        
        if usage_ratio >= critical_threshold:
            self.create_warning("CRITICAL", daily_total, daily_limit, current_usage)
        elif usage_ratio >= warning_threshold:
            self.create_warning("WARNING", daily_total, daily_limit, current_usage)
    
    def create_warning(self, level, daily_total, daily_limit, current_usage):
        """경고 파일 생성"""
        usage_ratio = daily_total / daily_limit
        remaining = daily_limit - daily_total
        
        warning_content = f"""# 🚨 Claude 토큰 사용량 {level}

**⚠️ 현재 상황**: {level.lower()} 레벨 도달

## 📊 사용량 현황
- **오늘 사용량**: {daily_total:,} / {daily_limit:,} 토큰 ({usage_ratio:.1%})
- **남은 토큰**: {remaining:,} 토큰
- **이번 작업**: {current_usage:,} 토큰

## 🎯 권장 조치

### {level} 단계 권장사항:
"""
        
        if level == "CRITICAL":
            warning_content += """
- 🛑 **즉시 작업 일시 중단** 권장
- 💾 현재 진행 상황을 HUB.md에 상세 기록
- 🔄 내일 작업 재개 계획 수립
- 📝 중요한 중간 결과물 저장

### 응급 상황시:
- 필수 작업만 간단히 완료
- 긴 분석이나 코드 생성 자제
- 간결한 답변 모드 활성화
"""
        else:  # WARNING
            warning_content += """
- ⚡ 토큰 사용량 최적화 필요
- 📋 불필요한 파일 읽기 최소화
- 🎯 핵심 작업에만 집중
- 💬 간결한 대화 모드 권장

### 최적화 방법:
- Subagent 적극 활용
- 긴 파일은 부분 읽기
- 중복 분석 방지
"""
        
        warning_content += f"""

## 📈 오늘의 사용 패턴
- **생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **세션 누적**: {self.get_session_total():,} 토큰

---
*이 파일은 자동 생성됩니다. 토큰 사용량이 안정되면 자동 삭제됩니다.*
"""
        
        with open(self.warning_file, 'w', encoding='utf-8') as f:
            f.write(warning_content)
        
        print(f"🚨 {level}: 토큰 사용량 {usage_ratio:.1%} 도달!")
        print(f"📄 상세 정보: {self.warning_file}")
    
    def get_status_report(self):
        """현재 상태 보고서 생성"""
        daily_total = self.get_daily_total()
        daily_limit = self.config["daily_limit"]
        usage_ratio = daily_total / daily_limit
        
        status = {
            "daily_used": daily_total,
            "daily_limit": daily_limit,
            "usage_ratio": usage_ratio,
            "remaining": daily_limit - daily_total,
            "status": "normal"
        }
        
        if usage_ratio >= self.config["critical_threshold"]:
            status["status"] = "critical"
        elif usage_ratio >= self.config["warning_threshold"]:
            status["status"] = "warning"
        
        return status
    
    def cleanup_old_logs(self, days_to_keep=30):
        """오래된 로그 정리"""
        if not self.log_file.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        temp_file = self.log_file.with_suffix('.tmp')
        
        with open(self.log_file, 'r', encoding='utf-8') as infile, \
             open(temp_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                try:
                    entry = json.loads(line.strip())
                    entry_date = datetime.fromisoformat(entry["timestamp"])
                    if entry_date >= cutoff_date:
                        outfile.write(line)
                except (json.JSONDecodeError, KeyError, ValueError):
                    # 잘못된 라인은 건너뛰기
                    continue
        
        temp_file.replace(self.log_file)

def estimate_tokens(text):
    """텍스트의 대략적인 토큰 수 추정"""
    # 간단한 추정: 평균 4자 = 1토큰
    return len(text) // 4

# CLI 실행을 위한 메인 함수
if __name__ == "__main__":
    import sys
    
    monitor = TokenMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            status = monitor.get_status_report()
            print(f"📊 토큰 사용량: {status['daily_used']:,} / {status['daily_limit']:,} ({status['usage_ratio']:.1%})")
            print(f"🔋 남은 토큰: {status['remaining']:,}")
            print(f"🚦 상태: {status['status']}")
        
        elif command == "log" and len(sys.argv) > 2:
            tokens = int(sys.argv[2])
            context = sys.argv[3] if len(sys.argv) > 3 else "manual"
            monitor.log_usage(tokens, context)
            print(f"✅ {tokens:,} 토큰 사용량 기록됨")
        
        elif command == "cleanup":
            monitor.cleanup_old_logs()
            print("🧹 오래된 로그 정리 완료")
        
        else:
            print("사용법: python token_monitor.py [status|log <tokens> [context]|cleanup]")
    else:
        # 기본: 상태 출력
        status = monitor.get_status_report()
        if status['status'] != 'normal':
            print(f"⚠️  토큰 {status['status'].upper()}: {status['usage_ratio']:.1%} 사용됨")
        else:
            print(f"✅ 토큰 사용량 정상: {status['usage_ratio']:.1%}")