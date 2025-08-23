#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 스크립트의 인코딩 문제를 완전히 해결합니다.
"""
import sys
import io
import os

def setup_utf8_encoding():
    """Python 실행 환경을 UTF-8로 강제 설정"""
    # stdout/stderr를 UTF-8로 재설정
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        # Python 3.6 이하 호환성
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 환경변수 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# 모든 스크립트 시작시 자동 실행
setup_utf8_encoding()

def safe_print(*args, **kwargs):
    """안전한 출력 함수 (유니코드 문자를 ASCII로 변환)"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 유니코드 문자를 안전한 형태로 변환
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # 문제가 되는 유니코드 문자들을 ASCII로 대체
                safe_arg = arg.replace('✅', '[OK]')
                safe_arg = safe_arg.replace('❌', '[ERROR]')
                safe_arg = safe_arg.replace('⚠️', '[WARN]')
                safe_arg = safe_arg.replace('🔌', '[CONNECT]')
                safe_arg = safe_arg.replace('📊', '[INFO]')
                safe_arg = safe_arg.replace('🔧', '[TOOL]')
                safe_arg = safe_arg.replace('💾', '[DATA]')
                safe_arg = safe_arg.replace('🎉', '[SUCCESS]')
                safe_arg = safe_arg.replace('•', '-')
                safe_arg = safe_arg.replace('‑', '-')
                safe_arg = safe_arg.replace('–', '-')
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

if __name__ == "__main__":
    safe_print("[OK] UTF-8 인코딩 설정 완료!")
    safe_print("[TEST] 유니코드 테스트: ✅ ❌ ⚠️ 🔌 📊")