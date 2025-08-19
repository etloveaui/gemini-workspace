#!/usr/bin/env python3
"""
자연어 명령 처리기
사용자의 자연어를 시스템 명령으로 변환
"""
import re
import json

class NaturalLanguageProcessor:
    def __init__(self):
        self.patterns = {
            r"상태.*확인|어떻게.*되|진행.*상황": "status",
            r"작업.*추가|새.*작업|할일.*추가": "add_task",
            r"검색|찾아|알아봐": "search",
            r"백업|저장": "backup",
            r"테스트|확인": "test"
        }
    
    def process(self, text: str) -> dict:
        """자연어 텍스트를 명령으로 변환"""
        for pattern, command in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    "command": command,
                    "original_text": text,
                    "confidence": 0.8
                }
        
        return {
            "command": "unknown", 
            "original_text": text,
            "confidence": 0.0
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        processor = NaturalLanguageProcessor()
        result = processor.process(" ".join(sys.argv[1:]))
        print(json.dumps(result, ensure_ascii=False, indent=2))
