#!/usr/bin/env python3
"""
인코딩 문제 방지 체크 스크립트
새 파일 생성 시 자동으로 UTF-8 확인
"""

import sys
import os
from pathlib import Path

def check_file_encoding(file_path):
    """파일 인코딩 확인"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # UTF-8 BOM 확인
        if raw_data.startswith(b'\xef\xbb\xbf'):
            return "UTF-8 BOM"
        
        # UTF-8 시도
        try:
            raw_data.decode('utf-8')
            return "UTF-8"
        except UnicodeDecodeError:
            pass
        
        # CP949 시도
        try:
            raw_data.decode('cp949')
            return "CP949"
        except UnicodeDecodeError:
            pass
        
        return "UNKNOWN"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    if len(sys.argv) < 2:
        print("사용법: python encoding_check.py <file_path>")
        return
    
    file_path = sys.argv[1]
    encoding = check_file_encoding(file_path)
    
    if encoding not in ["UTF-8", "UTF-8 BOM"]:
        print(f"[경고] {file_path}가 UTF-8이 아닙니다 (현재: {encoding})")
        print("UTF-8로 변환을 권장합니다.")
    else:
        print(f"[확인] {file_path}는 UTF-8입니다.")

if __name__ == "__main__":
    main()
