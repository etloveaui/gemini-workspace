#!/usr/bin/env python3
"""
지능형 에러 핸들러 v1.0 - Phase1 사용자 경험 개선
"무엇이 잘못됐고 어떻게 고칠지"를 명확히 알려주는 시스템
"""
import sys
import traceback
import json
from pathlib import Path
from datetime import datetime

class SmartErrorHandler:
    def __init__(self):
        self.root = Path("C:/Users/eunta/multi-agent-workspace")
        self.solutions_db = self.root / "docs" / "errors" / "solutions_db.json"
        self.error_log = self.root / "logs" / "errors.log"
        
        # 디렉토리 생성
        self.solutions_db.parent.mkdir(exist_ok=True, parents=True)
        self.error_log.parent.mkdir(exist_ok=True, parents=True)
        
        self.load_solutions_db()
    
    def load_solutions_db(self):
        """에러 해결 방안 데이터베이스 로드"""
        default_solutions = {
            "UnicodeDecodeError": {
                "description": "문자 인코딩 문제",
                "common_causes": [
                    "Windows에서 cp949와 UTF-8 인코딩 충돌",
                    "파일 인코딩 설정 문제"
                ],
                "solutions": [
                    "파일을 UTF-8로 저장 후 다시 시도",
                    "환경변수 PYTHONIOENCODING=utf-8 설정",
                    "subprocess 호출 시 encoding='utf-8' 추가"
                ],
                "prevention": "프로젝트 전체를 UTF-8로 설정 (.editorconfig, .vscode/settings.json)",
                "urgency": "medium"
            },
            "ModuleNotFoundError": {
                "description": "모듈을 찾을 수 없음",
                "common_causes": [
                    "필요한 패키지가 설치되지 않음",
                    "가상환경이 활성화되지 않음",
                    "Python 경로 문제"
                ],
                "solutions": [
                    "pip install [패키지명] 실행",
                    "가상환경 활성화: venv\\Scripts\\activate (Windows)",
                    "requirements.txt 확인 후 pip install -r requirements.txt"
                ],
                "prevention": "requirements.txt 파일 관리, 가상환경 사용",
                "urgency": "high"
            },
            "FileNotFoundError": {
                "description": "파일을 찾을 수 없음",
                "common_causes": [
                    "파일 경로가 잘못됨",
                    "파일이 존재하지 않음",
                    "권한 문제"
                ],
                "solutions": [
                    "파일 경로 다시 확인",
                    "파일이 실제로 존재하는지 확인",
                    "상대경로 대신 절대경로 사용"
                ],
                "prevention": "Path 객체 사용, exists() 확인",
                "urgency": "medium"
            },
            "PermissionError": {
                "description": "권한 부족",
                "common_causes": [
                    "관리자 권한 필요",
                    "파일이 다른 프로그램에서 사용중",
                    "읽기 전용 파일"
                ],
                "solutions": [
                    "관리자 권한으로 실행",
                    "파일을 사용중인 프로그램 종료",
                    "파일 속성에서 읽기 전용 해제"
                ],
                "prevention": "적절한 권한 설정, 파일 잠금 확인",
                "urgency": "high"
            }
        }
        
        if self.solutions_db.exists():
            try:
                with open(self.solutions_db, 'r', encoding='utf-8') as f:
                    self.solutions = json.load(f)
            except:
                self.solutions = default_solutions
        else:
            self.solutions = default_solutions
            self.save_solutions_db()
    
    def save_solutions_db(self):
        """솔루션 DB 저장"""
        with open(self.solutions_db, 'w', encoding='utf-8') as f:
            json.dump(self.solutions, f, indent=2, ensure_ascii=False)
    
    def handle_error(self, error_type, error_msg, context=""):
        """에러 지능형 처리"""
        print("=" * 60)
        print("🚨 ERROR DETECTED - 지능형 해결 방안 제시")
        print("=" * 60)
        
        # 에러 정보 출력
        print(f"오류 유형: {error_type}")
        print(f"오류 메시지: {error_msg}")
        if context:
            print(f"발생 상황: {context}")
        print()
        
        # 솔루션 찾기
        solution = self.find_solution(error_type)
        if solution:
            self.display_solution(solution)
        else:
            self.display_generic_help(error_type, error_msg)
        
        # 로그 기록
        self.log_error(error_type, error_msg, context)
    
    def find_solution(self, error_type):
        """에러 타입에 맞는 솔루션 찾기"""
        # 정확한 매칭
        if error_type in self.solutions:
            return self.solutions[error_type]
        
        # 부분 매칭
        for key, solution in self.solutions.items():
            if key.lower() in error_type.lower():
                return solution
        
        return None
    
    def display_solution(self, solution):
        """솔루션 표시"""
        print(f"📋 문제 설명: {solution['description']}")
        print()
        
        print("🔍 일반적인 원인:")
        for i, cause in enumerate(solution['common_causes'], 1):
            print(f"   {i}) {cause}")
        print()
        
        print("💡 해결 방법:")
        for i, sol in enumerate(solution['solutions'], 1):
            print(f"   {i}) {sol}")
        print()
        
        print(f"🛡️ 예방 방법: {solution['prevention']}")
        
        urgency = solution.get('urgency', 'medium')
        urgency_emoji = {'low': '🔵', 'medium': '🟡', 'high': '🔴'}
        print(f"{urgency_emoji.get(urgency, '🟡')} 긴급도: {urgency}")
    
    def display_generic_help(self, error_type, error_msg):
        """일반적인 도움말 표시"""
        print("❓ 알려지지 않은 오류입니다.")
        print()
        print("💡 일반적인 해결 방법:")
        print("   1) 오류 메시지를 자세히 읽어보세요")
        print("   2) 최근 변경사항을 되돌려보세요")
        print("   3) 가상환경을 재생성해보세요")
        print("   4) 관련 로그 파일을 확인해보세요")
        print()
        print("🔍 추가 도움이 필요하면:")
        print("   - docs/HUB.md에서 비슷한 문제를 찾아보세요")
        print("   - communication 폴더에 도움 요청 파일을 작성하세요")
    
    def log_error(self, error_type, error_msg, context):
        """에러 로그 기록"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_msg,
            "context": context
        }
        
        try:
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except:
            pass  # 로그 실패해도 메인 프로그램에 영향 주지 않음

def setup_global_error_handler():
    """전역 에러 핸들러 설정"""
    handler = SmartErrorHandler()
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """예외 처리 함수"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_type = exc_type.__name__
        error_msg = str(exc_value)
        
        # 컨텍스트 추출
        if exc_traceback:
            tb_lines = traceback.format_tb(exc_traceback)
            context = tb_lines[-1].strip() if tb_lines else ""
        else:
            context = ""
        
        handler.handle_error(error_type, error_msg, context)
    
    sys.excepthook = handle_exception
    return handler

def main():
    """테스트 실행"""
    print("🧪 지능형 에러 핸들러 테스트")
    
    # 전역 핸들러 설정
    handler = setup_global_error_handler()
    
    print("✅ 전역 에러 핸들러 활성화됨")
    print("이제 모든 에러가 지능형으로 처리됩니다.")
    
    # 테스트 에러 발생
    print("\n📝 테스트 에러 시뮬레이션:")
    handler.handle_error("UnicodeDecodeError", "cp949 codec can't decode byte", "subprocess 실행 중")

if __name__ == "__main__":
    main()