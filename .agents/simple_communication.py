#!/usr/bin/env python3
"""
단일 파일 대화 방식 - 토큰 효율적 커뮤니케이션
사용자가 간단하게 줄글로 작성하면 자동으로 정리해주는 시스템
"""

import os
import re
from datetime import datetime
from pathlib import Path

class SimpleCommunication:
    def __init__(self, workspace_path="."):
        self.workspace = Path(workspace_path)
        self.comm_dir = self.workspace / "communication"
        
    def process_simple_input(self, text: str, agent: str = "claude") -> str:
        """간단한 텍스트를 구조화된 마크다운으로 변환"""
        
        # 현재 날짜/시간
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        # 우선순위 자동 감지
        priority = "P2"  # 기본
        if any(word in text.lower() for word in ["긴급", "urgent", "즉시", "문제", "오류", "에러"]):
            priority = "P0"
        elif any(word in text.lower() for word in ["중요", "important", "빠르게", "먼저"]):
            priority = "P1"
        
        # 태그 자동 감지
        tags = []
        if "오류" in text or "에러" in text or "문제" in text:
            tags.append("bugfix")
        if "개선" in text or "최적화" in text:
            tags.append("improvement")
        if "추가" in text or "구현" in text:
            tags.append("feature")
        if "정리" in text or "삭제" in text:
            tags.append("cleanup")
        
        if not tags:
            tags = ["general"]
        
        # 구조화된 마크다운 생성
        markdown = f"""---
agent: {agent}
priority: {priority}
status: pending
tags: {tags}
created: {date_str} {time_str}
---

# 요청사항

## 💬 내용
{text}

## 📊 진행상황
- [ ] 분석 시작
- [ ] 작업 진행
- [ ] 완료

---
자동 생성됨: {now.strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return markdown
    
    def save_to_file(self, content: str, agent: str = "claude") -> Path:
        """파일로 저장하고 경로 반환"""
        now = datetime.now()
        filename = f"{now.strftime('%Y%m%d_%H%M%S')}_auto.md"
        
        agent_dir = self.comm_dir / agent
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = agent_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

# CLI 사용법
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python simple_communication.py '요청내용'")
        print("예시: python simple_communication.py '커밋 오류 해결해줘'")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    comm = SimpleCommunication()
    
    markdown = comm.process_simple_input(text)
    file_path = comm.save_to_file(markdown)
    
    print(f"✅ 파일 생성: {file_path}")
    print("내용:")
    print(markdown)