#!/usr/bin/env python3
"""
반복 오류 방지 시스템
- 자주 발생하는 오류들을 데이터베이스에 기록
- 동일한 오류 재발 시 자동 해결책 제시
- Windows 환경 최적화 솔루션 제공
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

class ErrorPrevention:
    def __init__(self, workspace_path="."):
        self.workspace = Path(workspace_path)
        self.db_path = self.workspace / ".agents" / "error_prevention.db"
        self.init_database()
        
        # 알려진 오류 패턴과 해결책
        self.known_errors = {
            "del_command_not_found": {
                "pattern": "del: command not found",
                "solution": "python -c \"import os; os.remove('{filename}')\"",
                "description": "Windows에서 del 명령어 대신 Python 사용"
            },
            "unicode_decode_error": {
                "pattern": "UnicodeDecodeError.*cp949",
                "solution": "subprocess.run(..., encoding='utf-8', errors='ignore')",
                "description": "Windows 인코딩 문제 - UTF-8 강제 사용"
            },
            "precommit_hook_error": {
                "pattern": "AttributeError.*NoneType.*splitlines",
                "solution": "precommit hook 인코딩 수정 적용됨",
                "description": "Git hook stdout가 None인 경우 처리"
            },
            "nul_file_error": {
                "pattern": "error: invalid path 'nul'",
                "solution": "git add 시 nul 파일 제외 또는 삭제",
                "description": "Windows nul 파일 Git 추가 불가"
            },
            "commit_encoding_error": {
                "pattern": "can't decode byte.*in position.*illegal multibyte sequence",
                "solution": "SKIP_DIFF_CONFIRM=1 설정 또는 GUI 도구 사용",
                "description": "Git 커밋 시 한글 메시지 인코딩 문제"
            }
        }
    
    def init_database(self):
        """오류 추적 데이터베이스 초기화"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_hash TEXT UNIQUE,
                error_pattern TEXT,
                error_message TEXT,
                solution TEXT,
                occurrence_count INTEGER DEFAULT 1,
                first_seen DATETIME,
                last_seen DATETIME,
                auto_resolved BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        conn.close()
    
    def hash_error(self, error_text: str) -> str:
        """오류 텍스트의 해시 생성"""
        # 경로나 시간 등 가변적인 부분 제거 후 해시
        cleaned = error_text.lower()
        # 경로 정규화
        cleaned = cleaned.replace(str(self.workspace).lower(), "[workspace]")
        cleaned = cleaned.replace("c:\\users\\", "[userdir]\\")
        
        return hashlib.md5(cleaned.encode()).hexdigest()
    
    def detect_error_pattern(self, error_text: str) -> dict:
        """오류 패턴 감지"""
        for error_id, error_info in self.known_errors.items():
            import re
            if re.search(error_info["pattern"], error_text, re.IGNORECASE):
                return {
                    "id": error_id,
                    "pattern": error_info["pattern"],
                    "solution": error_info["solution"],
                    "description": error_info["description"]
                }
        return None
    
    def log_error(self, error_text: str, auto_resolved: bool = False):
        """오류 로깅"""
        error_hash = self.hash_error(error_text)
        detected = self.detect_error_pattern(error_text)
        
        conn = sqlite3.connect(self.db_path)
        
        # 기존 기록 확인
        cursor = conn.cursor()
        cursor.execute("SELECT occurrence_count FROM error_log WHERE error_hash = ?", (error_hash,))
        existing = cursor.fetchone()
        
        now = datetime.now()
        
        if existing:
            # 기존 기록 업데이트
            new_count = existing[0] + 1
            cursor.execute("""
                UPDATE error_log 
                SET occurrence_count = ?, last_seen = ?, auto_resolved = ?
                WHERE error_hash = ?
            """, (new_count, now, auto_resolved, error_hash))
        else:
            # 새 기록 추가
            solution = detected["solution"] if detected else "수동 해결 필요"
            pattern = detected["pattern"] if detected else "알 수 없는 패턴"
            
            cursor.execute("""
                INSERT INTO error_log 
                (error_hash, error_pattern, error_message, solution, first_seen, last_seen, auto_resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (error_hash, pattern, error_text[:500], solution, now, now, auto_resolved))
        
        conn.commit()
        conn.close()
        
        return detected
    
    def get_solution(self, error_text: str) -> dict:
        """오류에 대한 해결책 제공"""
        detected = self.detect_error_pattern(error_text)
        
        if detected:
            self.log_error(error_text, auto_resolved=True)
            return {
                "found": True,
                "solution": detected["solution"],
                "description": detected["description"],
                "auto_fix": True
            }
        else:
            self.log_error(error_text, auto_resolved=False)
            return {
                "found": False,
                "message": "새로운 오류 패턴입니다. 수동 해결이 필요합니다.",
                "auto_fix": False
            }
    
    def get_frequent_errors(self, limit=10):
        """자주 발생하는 오류 목록"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT error_pattern, error_message, solution, occurrence_count, last_seen
            FROM error_log 
            ORDER BY occurrence_count DESC 
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "pattern": row[0],
                "message": row[1],
                "solution": row[2],
                "count": row[3],
                "last_seen": row[4]
            }
            for row in results
        ]
    
    def create_prevention_guide(self):
        """오류 방지 가이드 생성"""
        frequent_errors = self.get_frequent_errors()
        
        guide = """# 오류 방지 가이드

## 🚨 자주 발생하는 오류들

"""
        
        for i, error in enumerate(frequent_errors, 1):
            guide += f"""### {i}. {error['pattern']} ({error['count']}회 발생)

**마지막 발생**: {error['last_seen']}

**해결책**: 
```
{error['solution']}
```

---

"""
        
        guide += """## ⚡ 자동 해결 시스템

이 시스템은 다음과 같이 작동합니다:

1. **오류 감지**: 알려진 패턴 자동 인식
2. **해결책 제시**: 즉시 해결 명령어 제공  
3. **학습**: 새로운 오류 패턴 데이터베이스에 저장
4. **예방**: 동일 오류 재발 시 자동 해결

## 🔧 수동 해결이 필요한 경우

1. `python .agents/error_prevention.py analyze "오류메시지"`
2. 해결책 확인 후 적용
3. 성공 시 자동으로 데이터베이스에 기록
"""
        
        guide_path = self.workspace / "ERROR_PREVENTION_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        return guide_path

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    ep = ErrorPrevention()
    
    if len(sys.argv) < 2:
        print("사용법: python error_prevention.py <command> [args...]")
        print("명령어:")
        print("  analyze <error_text>  - 오류 분석 및 해결책 제시")
        print("  frequent             - 자주 발생하는 오류 목록")
        print("  guide                - 오류 방지 가이드 생성")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("사용법: analyze <error_text>")
            sys.exit(1)
        
        error_text = " ".join(sys.argv[2:])
        result = ep.get_solution(error_text)
        
        if result["found"]:
            print(f"✅ 알려진 오류 패턴 감지")
            print(f"📋 해결책: {result['solution']}")
            print(f"💡 설명: {result['description']}")
        else:
            print(f"❓ 새로운 오류 패턴")
            print(f"📝 {result['message']}")
    
    elif command == "frequent":
        errors = ep.get_frequent_errors()
        print("🔥 자주 발생하는 오류들:")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error['pattern']} ({error['count']}회)")
    
    elif command == "guide":
        guide_path = ep.create_prevention_guide()
        print(f"📄 가이드 생성: {guide_path}")
    
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)