#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인코딩 문제 해결 스크립트
- UTF-8로 파일 재저장
- 깨진 문자 복구 시도
"""

import os
import sys
from pathlib import Path

def fix_file_encoding(file_path: Path):
    """파일 인코딩 문제 수정"""
    try:
        # 여러 인코딩으로 읽기 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        
        content = None
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"[성공] {encoding}으로 읽기 성공: {file_path}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"[실패] 모든 인코딩 시도 실패: {file_path}")
            return False
        
        # UTF-8로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[수정완료] UTF-8로 저장: {file_path}")
        return True
        
    except Exception as e:
        print(f"[오류] {file_path}: {e}")
        return False

if __name__ == "__main__":
    # prompt1 파일 수정
    prompt1_path = Path("communication/claude/20250820_prompt1.md")
    
    if prompt1_path.exists():
        print("WSL 인코딩 문제 수정 중...")
        fix_file_encoding(prompt1_path)
    else:
        print("prompt1 파일을 찾을 수 없습니다.")