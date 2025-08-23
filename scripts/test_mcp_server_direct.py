#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 서버 직접 테스트
"""
import subprocess
import sys
import time
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_mcp_server_process(server_script):
    """MCP 서버 프로세스 테스트"""
    server_path = ROOT / "src" / "ai_integration" / "mcp_servers" / server_script
    
    try:
        print(f"[TEST] {server_script} 프로세스 시작...")
        
        # 프로세스 시작
        proc = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )
        
        # 프로세스가 시작되는지 확인
        time.sleep(1)
        
        if proc.poll() is None:
            print(f"[OK] {server_script} 프로세스 실행 중")
            
            # MCP 초기화 메시지 전송 시도
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            try:
                proc.stdin.write(json.dumps(init_message) + "\n")
                proc.stdin.flush()
                
                # 잠시 대기
                time.sleep(0.5)
                
                print(f"[OK] {server_script} 초기화 메시지 전송됨")
                
            except Exception as e:
                print(f"[WARN] {server_script} 메시지 전송 실패: {e}")
            
            # 프로세스 종료
            proc.terminate()
            proc.wait(timeout=2)
            
            return True
        else:
            stderr_output = proc.stderr.read()
            print(f"[ERROR] {server_script} 프로세스 즉시 종료")
            if stderr_output:
                print(f"  stderr: {stderr_output}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {server_script} 테스트 실패: {e}")
        return False

def main():
    print("=== MCP 서버 프로세스 테스트 ===")
    print()
    
    servers = ["filesystem_server.py", "workspace_server.py"]
    results = {}
    
    for server in servers:
        results[server] = test_mcp_server_process(server)
        print()
    
    print("=== 테스트 결과 ===")
    for server, success in results.items():
        status = "성공" if success else "실패"
        print(f"{server}: {status}")
    
    all_success = all(results.values())
    if all_success:
        print("\n[SUCCESS] 모든 MCP 서버가 프로세스로 실행 가능합니다!")
    else:
        print("\n[ERROR] 일부 MCP 서버에 문제가 있습니다.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)