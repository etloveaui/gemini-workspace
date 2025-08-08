import subprocess, sys, json
from pathlib import Path

# 금지된 코드 패턴 목록 (GEMINI.md 규칙에 기반)
FORBIDDEN_PATTERNS = [
    "datetime.utcnow",  # TZ 미고려 datetime 사용 금지
    "TODO:",            # 남은 TODO 주석 금지
    "print(",           # 디버깅 print 사용 지양
    "shell=True"        # 서브프로세스 호출시 shell=True 사용 금지 (Windows-first 원칙)
]

def scan_outdated_pip():
    """
    pip 통해 현재 설치된 패키지 중 업데이트 가능한 목록을 반환.
    반환 형식: [{'name': 패키지명, 'current': 현버전, 'latest': 최신버전}, ...]
    """
    try:
        # pip list --outdated를 JSON 포맷으로 실행
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format", "json"],
            check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        # pip 실행 오류 시 빈 목록 반환
        return []
    try:
        outdated_list = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    updates = []
    for item in outdated_list:
        name = item.get("name")
        current = item.get("version")
        latest = item.get("latest_version")
        if name and current and latest:
            updates.append({"name": name, "current": current, "latest": latest})
    return updates

def scan_deprecations():
    """
    최근 pytest 실행 로그를 통해 DeprecationWarning 메시지를 수집.
    반환 형식: ['경고메시지1', '경고메시지2', ...]
    """
    warnings = []
    try:
        # pytest를 조용한 모드(-q)로 실행하여 DeprecationWarning 출력 수집
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-W", "default"],
            check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        # 테스트 실패 등으로 프로세스가 비정상 종료해도 경고는 수집 (stdout 사용)
        output = e.stdout or ""
    else:
        output = result.stdout or ""
    # 출력에서 "DeprecationWarning" 포함된 라인 수집
    for line in output.splitlines():
        if "DeprecationWarning" in line:
            # "DeprecationWarning: " 이후 부분만 추출하여 메시지로 저장
            if "DeprecationWarning:" in line:
                msg = line.split("DeprecationWarning:")[1].strip()
            else:
                msg = line.strip()
            if msg and msg not in warnings:
                warnings.append(msg)
    return warnings

def scan_rule_violations(base_dir=None):
    """
    프로젝트 코드 내 금지된 패턴 사용을 스캔하여 위반 사항 목록을 반환.
    base_dir 지정 시 해당 경로 하위만 검사하며, 기본(None)이면 레포지토리 루트에서 검사.
    반환 형식: [{'file': 파일경로, 'pattern': 패턴문자열, 'line': 줄번호}, ...]
    """
    violations = []
    # 검사 기준 디렉토리 설정
    if base_dir:
        root_path = Path(base_dir)
    else:
        # 현재 스크립트의 상위 2단계를 레포지토리 루트로 간주
        root_path = Path(__file__).resolve().parents[2]
    # 모든 파이썬 파일 순회
    for filepath in root_path.rglob("*.py"):
        try:
            text = filepath.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            continue  # 읽기 실패시 건너뛰기
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pat in FORBIDDEN_PATTERNS:
                if pat in line:
                    violations.append({
                        "file": str(filepath.relative_to(root_path)),
                        "pattern": pat,
                        "line": lineno
                    })
    return violations

def scan_all():
    """
    모든 스캔 기능을 수행하여 종합 결과를 반환.
    반환 형식: {'outdated': [...], 'warnings': [...], 'violations': [...]}
    """
    return {
        "outdated": scan_outdated_pip(),
        "warnings": scan_deprecations(),
        "violations": scan_rule_violations()
    }

# 스크립트를 직접 실행했을 때의 동작 (예: invoke auto.scan이 호출될 경우)
if __name__ == "__main__":
    results = scan_all()
    # JSON 형식으로 출력하여 propose 단계 등에서 활용하거나 로그 남김
    print(json.dumps(results, indent=2, ensure_ascii=False))
