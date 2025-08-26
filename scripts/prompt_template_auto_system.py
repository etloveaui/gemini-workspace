#!/usr/bin/env python3
"""
프롬프트 템플릿 자동화 시스템
- 첫 접속 시 모든 에이전트 폴더에 날짜별 프롬프트 템플릿 자동 생성
- 네이밍 룰 통일: YYYYMMDD_NN_prompt.md
- 모든 에이전트(Claude, Codex, Gemini) 동시 적용
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime
import json
import shutil

# 환경 경로 관리 시스템 사용
from environment_path_manager import get_workspace_path

def check_if_first_access_today(agent: str) -> bool:
    """오늘 첫 접속인지 확인"""
    agent_dir = get_workspace_path("communication", agent)
    if not agent_dir.exists():
        agent_dir.mkdir(parents=True, exist_ok=True)
        return True
    
    today = datetime.now().strftime("%Y%m%d")
    
    # 오늘 날짜로 시작하는 파일이 있는지 확인
    existing_today_files = list(agent_dir.glob(f"{today}_*_prompt.md"))
    return len(existing_today_files) == 0

def get_next_sequence_number(agent: str) -> str:
    """다음 시퀀스 번호 획득 (01, 02, 03...)"""
    agent_dir = get_workspace_path("communication", agent)
    today = datetime.now().strftime("%Y%m%d")
    
    # 오늘 날짜로 시작하는 모든 파일 찾기
    existing_files = list(agent_dir.glob(f"{today}_*_prompt.md"))
    
    if not existing_files:
        return "01"
    
    # 시퀀스 번호 추출하여 최대값 찾기
    max_seq = 0
    for file_path in existing_files:
        # 패턴: YYYYMMDD_NN_prompt.md
        parts = file_path.stem.split('_')
        if len(parts) >= 2:
            try:
                seq_num = int(parts[1])
                max_seq = max(max_seq, seq_num)
            except ValueError:
                continue
    
    return f"{max_seq + 1:02d}"

def get_agent_template_content(agent: str) -> str:
    """에이전트별 템플릿 내용 생성"""
    base_template = """---
agent: {agent}
priority: P0|P1|P2|P3
status: pending
created: {timestamp}
---

# {agent_title} 작업 요청

## 📋 작업 개요
- **작업명**: [작업 제목]
- **우선순위**: [P0-긴급|P1-높음|P2-일반|P3-낮음]
- **예상 소요시간**: [시간]
- **담당자**: {agent_title} ({agent_role})

## 🎯 작업 상세

### 요청 내용
1. [요청사항 1]
2. [요청사항 2]
3. [요청사항 3]

### 배경 정보
- **현재 상황**: 
- **해결해야 할 문제**: 
- **제약 조건**: 

### 관련 파일
- `파일 경로 1`: 설명
- `파일 경로 2`: 설명

### 기대 결과
- **최종 산출물**: 
- **품질 기준**: 
- **성공 기준**: 

## 📊 진행 상황

### Todo 리스트
- [ ] 작업 1
- [ ] 작업 2  
- [ ] 작업 3

### 완료 내용
- ✅ [완료일시] 완료 내용

## 💬 {agent_title} 응답

### [응답 시간] 작업 분석 및 계획

[{agent_title}의 분석 및 실행 계획]

### [완료 시간] ✅ 작업 완료

[최종 결과 및 산출물 요약]

---

**💡 사용법**: 이 템플릿을 복사하여 새로운 작업 요청 파일을 생성하세요.
"""
    
    agent_configs = {
        "claude": {
            "title": "Claude",
            "role": "총감독관"
        },
        "codex": {
            "title": "Codex", 
            "role": "코딩 전문가"
        },
        "gemini": {
            "title": "Gemini",
            "role": "시스템 분석가"
        }
    }
    
    config = agent_configs.get(agent.lower(), {"title": agent.title(), "role": "AI 어시스턴트"})
    
    return base_template.format(
        agent=agent.lower(),
        agent_title=config["title"],
        agent_role=config["role"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

def create_prompt_template_for_agent(agent: str) -> tuple:
    """특정 에이전트에 대한 프롬프트 템플릿 생성"""
    try:
        # 네이밍 룰: YYYYMMDD_NN_prompt.md
        today = datetime.now().strftime("%Y%m%d")
        sequence = get_next_sequence_number(agent)
        filename = f"{today}_{sequence}_prompt.md"
        
        # 경로 생성
        agent_dir = get_workspace_path("communication", agent)
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        template_path = agent_dir / filename
        
        # 템플릿 내용 생성
        template_content = get_agent_template_content(agent)
        
        # 파일 작성
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return True, str(template_path)
        
    except Exception as e:
        return False, str(e)

def run_auto_prompt_template_creation():
    """모든 에이전트에 대한 자동 프롬프트 템플릿 생성"""
    print("🚀 프롬프트 템플릿 자동화 시스템")
    print("=" * 50)
    
    agents = ["claude", "codex", "gemini"]
    results = []
    
    for agent in agents:
        print(f"\n📝 {agent.upper()} 프롬프트 템플릿 확인...")
        
        if check_if_first_access_today(agent):
            print(f"  → 오늘 첫 접속 감지, 템플릿 생성 중...")
            success, result = create_prompt_template_for_agent(agent)
            
            if success:
                print(f"  ✅ 생성 완료: {Path(result).name}")
                results.append({
                    "agent": agent,
                    "status": "created",
                    "file": result
                })
            else:
                print(f"  ❌ 생성 실패: {result}")
                results.append({
                    "agent": agent,
                    "status": "failed",
                    "error": result
                })
        else:
            print(f"  ✅ 오늘 이미 접속함, 건너뛰기")
            results.append({
                "agent": agent,
                "status": "skipped",
                "reason": "already_exists"
            })
    
    # 결과 요약
    print(f"\n📊 결과 요약:")
    created_count = sum(1 for r in results if r["status"] == "created")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    
    print(f"  - 생성: {created_count}개")
    print(f"  - 실패: {failed_count}개")
    print(f"  - 건너뛰기: {skipped_count}개")
    
    # 실패한 경우 상세 정보
    if failed_count > 0:
        print(f"\n❌ 실패 상세:")
        for result in results:
            if result["status"] == "failed":
                print(f"  - {result['agent']}: {result['error']}")
    
    return results

def force_create_all_templates():
    """강제로 모든 에이전트 템플릿 생성 (테스트용)"""
    print("🔥 강제 템플릿 생성 모드")
    agents = ["claude", "codex", "gemini"]
    results = []
    
    for agent in agents:
        success, result = create_prompt_template_for_agent(agent)
        results.append({
            "agent": agent,
            "success": success,
            "result": result
        })
        
        status = "✅" if success else "❌"
        print(f"{status} {agent.upper()}: {Path(result).name if success else result}")
    
    return results

def get_template_status_report():
    """템플릿 상태 리포트"""
    print("📋 프롬프트 템플릿 상태 리포트")
    print("=" * 50)
    
    agents = ["claude", "codex", "gemini"]
    today = datetime.now().strftime("%Y%m%d")
    
    for agent in agents:
        agent_dir = get_workspace_path("communication", agent)
        
        if not agent_dir.exists():
            print(f"❌ {agent.upper()}: 폴더 없음")
            continue
        
        # 오늘 템플릿들
        today_templates = list(agent_dir.glob(f"{today}_*_prompt.md"))
        
        # 전체 템플릿들
        all_templates = list(agent_dir.glob("*_prompt.md"))
        
        print(f"📝 {agent.upper()}:")
        print(f"  - 오늘: {len(today_templates)}개")
        print(f"  - 전체: {len(all_templates)}개")
        
        if today_templates:
            print("  - 오늘 파일들:")
            for template in sorted(today_templates):
                print(f"    • {template.name}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--force":
            force_create_all_templates()
        elif command == "--status":
            get_template_status_report()
        elif command == "--help":
            print("프롬프트 템플릿 자동화 시스템")
            print("사용법:")
            print("  python prompt_template_auto_system.py           # 자동 실행")
            print("  python prompt_template_auto_system.py --force   # 강제 생성")
            print("  python prompt_template_auto_system.py --status  # 상태 확인")
        else:
            print(f"알 수 없는 명령어: {command}")
    else:
        # 기본 자동 실행
        run_auto_prompt_template_creation()