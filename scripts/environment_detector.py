#!/usr/bin/env python3
"""
환경 감지 시스템 - 토큰을 절약하면서 작업 위치 파악 (단순 텍스트 출력)
집/회사/노트북 등 여러 위치에서 작업할 때 자동으로 환경을 감지
"""
import os
import platform
import socket
import json
from pathlib import Path
from datetime import datetime
from cli_style import header, section, item, kv

def detect_environment():
    """현재 작업 환경을 감지하고 기록"""
    
    # 기본 시스템 정보
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "user": os.getenv('USERNAME', os.getenv('USER', 'unknown')),
        "working_directory": str(Path.cwd()),
    }
    
    # 네트워크 정보 (간단히)
    try:
        system_info["local_ip"] = socket.gethostbyname(socket.gethostname())
    except:
        system_info["local_ip"] = "unknown"
    
    # 특별한 환경 감지 (회사/집/노트북 구분)
    environment_hints = {
        "is_company": False,
        "is_home": False,
        "is_laptop": False,
        "location_hints": []
    }
    
    hostname = system_info["hostname"].lower()
    
    # 호스트명으로 환경 추정
    if any(word in hostname for word in ['desktop', 'pc', 'work', 'office']):
        environment_hints["is_company"] = True
        environment_hints["location_hints"].append("company_desktop")
    elif any(word in hostname for word in ['laptop', 'book', 'mobile']):
        environment_hints["is_laptop"] = True
        environment_hints["location_hints"].append("laptop")
    elif any(word in hostname for word in ['home', 'personal']):
        environment_hints["is_home"] = True
        environment_hints["location_hints"].append("home")
    
    # 드라이브 구성으로 추정 (Windows)
    if platform.system() == "Windows":
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{letter}:"):
                drives.append(letter)
        environment_hints["available_drives"] = drives
        
        # 회사 환경은 보통 더 많은 드라이브가 마운트됨
        if len(drives) > 3:
            environment_hints["location_hints"].append("likely_company")
    
    # 설치된 소프트웨어로 추정
    software_hints = []
    if os.path.exists(r"C:\Program Files\Microsoft Office"):
        software_hints.append("office_suite")
    if os.path.exists(r"C:\Program Files\Git"):
        software_hints.append("git_installed")
    
    environment_hints["software_hints"] = software_hints
    
    # 현재 시간으로 추정 (업무 시간대면 회사일 가능성)
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 18:
        environment_hints["location_hints"].append("business_hours")
    
    result = {
        "system": system_info,
        "environment": environment_hints,
        "confidence": calculate_confidence(environment_hints)
    }
    
    return result

def calculate_confidence(hints):
    """환경 추정 신뢰도 계산"""
    confidence = {
        "company": 0,
        "home": 0,
        "laptop": 0
    }
    
    for hint in hints["location_hints"]:
        if "company" in hint or "business" in hint:
            confidence["company"] += 30
        if "home" in hint:
            confidence["home"] += 30
        if "laptop" in hint:
            confidence["laptop"] += 40
    
    if hints["is_company"]:
        confidence["company"] += 50
    if hints["is_home"]:
        confidence["home"] += 50
    if hints["is_laptop"]:
        confidence["laptop"] += 50
    
    return confidence

def save_environment_profile():
    """환경 프로필을 저장"""
    root = Path(__file__).parent.parent
    profiles_dir = root / ".agents" / "environment_profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    env_data = detect_environment()
    
    # 호스트명 기반 파일명
    hostname = env_data["system"]["hostname"]
    profile_file = profiles_dir / f"{hostname}.json"
    
    with open(profile_file, 'w', encoding='utf-8') as f:
        json.dump(env_data, f, indent=2, ensure_ascii=False)
    
    print(header("Environment Profile"))
    print(kv("Saved", profile_file))
    return env_data

def get_current_environment_summary():
    """현재 환경의 간단한 요약 (토큰 절약용)"""
    env = detect_environment()
    
    confidence = env["confidence"]
    best_guess = max(confidence.items(), key=lambda x: x[1])
    
    summary = {
        "location": best_guess[0] if best_guess[1] > 30 else "unknown",
        "confidence": best_guess[1],
        "hostname": env["system"]["hostname"],
        "time": datetime.now().strftime("%H:%M")
    }
    
    return summary

if __name__ == "__main__":
    # 환경 감지 및 저장
    profile = save_environment_profile()

    # 간단한 요약 출력
    summary = get_current_environment_summary()
    print(section("Environment Summary"))
    print(kv("Location", f"{summary['location']} ({summary['confidence']}%)"))
    print(kv("Hostname", summary['hostname']))
    print(kv("Time", summary['time']))
