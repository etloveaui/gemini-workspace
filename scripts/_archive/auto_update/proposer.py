import json, datetime
from pathlib import Path
# scanner 모듈 import (동일 패키지에 있으므로 상대 경로 가능)
try:
    # scanner.py가 같은 패키지에 존재한다고 가정
    from . import scanner
except ImportError:
    import scanner

def generate_proposal_content(scan_results):
    """
    스캔 결과를 입력 받아 WHAT/WHY/HOW 형식의 제안서 마크다운 콘텐츠를 생성.
    반환값: str (마크다운 텍스트)
    """
    lines = []
    # 헤더 작성
    today = datetime.date.today().strftime("%Y-%m-%d")
    lines.append(f"# Self-Update Proposals ({today})\n")
    lines.append("Gemini-CLI 시스템이 자동 생성한 자가 개선 제안 목록입니다. 각 제안은 WHAT/WHY/HOW 형식으로 구성되어 있습니다.\n")

    # 1. 패키지 업데이트 제안 섹션
    outdated_list = scan_results.get("outdated") or []
    if outdated_list:
        lines.append("## 의존성 업데이트 제안\n")
        for pkg in outdated_list:
            name = pkg["name"]; current = pkg["current"]; latest = pkg["latest"]
            lines.append(f"### 패키지 업그레이드: **{name}** {current} → {latest}")
            lines.append(f"**WHAT:** `{name}` 패키지를 버전 **{latest}**(으)로 업그레이드합니다.")
            # WHY: 주된 이유 (패치, 마이너 업뎃 구분)
            if latest.split('.')[0] != current.split('.')[0]:
                # major 버전 변경
                lines.append(f"**WHY:** 해당 패키지의 주요 업데이트가 발견되었습니다. 새로운 주요 버전({latest})으로 업그레이드하여 최신 호환성과 기능을 적용합니다.")
            elif latest.split('.')[1] != current.split('.')[1]:
                # minor 버전 변경
                lines.append(f"**WHY:** 기능 추가나 개선 사항을 포함한 업데이트({current} → {latest})가 존재합니다. 부버전 업그레이드로 성능 및 기능 개선을 누릴 수 있습니다.")
            else:
                # patch 버전 변경
                lines.append(f"**WHY:** 현재 버전에 대한 버그 수정이나 보안 패치({current} → {latest})가 release되었습니다. 안정성 강화를 위해 패치 버전을 적용합니다.")
            lines.append(f"**HOW:** `pip install -U {name}` 명령을 실행하여 패키지를 업그레이드합니다. 업그레이드 후 모든 테스트를 돌려 호환성 검증을 진행합니다.\n")
    else:
        lines.append("## 의존성 업데이트 제안\n(업데이트 필요한 pip 패키지가 발견되지 않았습니다.)\n")

    # 2. Deprecation 경고 대응 제안 섹션
    warnings = scan_results.get("warnings") or []
    if warnings:
        lines.append("## Deprecation 경고 대응 제안\n")
        for msg in warnings:
            # 경고 메시지에서 가능한 핵심 키워드 추출 (콜론 앞 내용 등)
            short_desc = msg.split('.')[0].strip()
            lines.append(f"### Deprecation 해결: *{short_desc}*")
            lines.append(f"**WHAT:** 코드에 나타나는 Deprecation 경고 (`{msg}`)를 해결합니다.")
            lines.append(f"**WHY:** 해당 경고는 앞으로 지원이 중단될 기능을 사용하고 있음을 의미합니다. 지금 코드를 수정해 두면 미래 호환성 문제가 예방되고, 불필요한 콘솔 경고를 없앨 수 있습니다.")
            lines.append(f"**HOW:** 권장되는 대체 API로 코드를 수정합니다. 예를 들어, 위 경고의 경우 deprecated 된 함수를 새로운 함수로 교체하고 관련된 인자나 호출방식을 업데이트합니다. 수정 후 테스트를 돌려 경고가 사라졌음을 확인합니다.\n")
    else:
        lines.append("## Deprecation 경고 대응 제안\n(새로운 DeprecationWarning 항목이 발견되지 않았습니다.)\n")

    # 3. 코드 규칙 위반 수정 제안 섹션
    violations = scan_results.get("violations") or []
    if violations:
        # 패턴 종류별로 그룹화하여 제안 작성
        lines.append("## 코드 규칙 위반 수정 제안\n")
        # 그룹화: 패턴 문자열 -> 해당 발생 목록
        grouped = {}
        for v in violations:
            pat = v["pattern"]; file = v["file"]; line = v["line"]
            grouped.setdefault(pat, []).append(f"{file} (Line {line})")
        for pat, locations in grouped.items():
            if "print(" in pat:
                title = "불필요한 print문 제거"
                what_desc = "`print()` 호출을 제거하거나 적절한 logging으로 대체"
                why_desc = "print문은 디버깅 용도로 남은 것으로 추정되며, 지속 사용시 불필요한 콘솔 출력이나 정보 유출 우려가 있습니다."
                how_desc = "`print` 호출을 삭제하거나 `logging` 모듈을 활용하도록 변경합니다."
            elif "TODO:" in pat:
                title = "남은 TODO 주석 처리"
                what_desc = "코드 내 남은 TODO 주석을 처리 또는 제거"
                why_desc = "TODO 주석은 구현되지 않은 작업을 나타냅니다. 방치된 TODO는 코드 품질을 저해하고 추적 어려움을 줍니다."
                how_desc = "해당 TODO의 작업을 구현 완료하거나, 불필요한 경우 주석을 제거합니다."
            elif "datetime.utcnow" in pat:
                title = "datetime.utcnow 사용 개선"
                what_desc = "`datetime.utcnow()` 대신 시간대(timezone)를 고려한 현재 시간 사용"
                why_desc = "현재 코드에서 TZ 정보 없는 UTC now를 사용하고 있습니다. 이는 Windows-first 보안/시간대 정책에 어긋납니다."
                how_desc = "`datetime.now(timezone.utc)` 등을 사용하여 명시적으로 UTC 시간대 객체를 사용하거나, 적절한 지역 시간대로 변경합니다."
            elif "shell=True" in pat:
                title = "서브프로세스 호출 시 shell=True 지양"
                what_desc = "subprocess 호출에서 `shell=True` 옵션 제거"
                why_desc = "Windows-first 원칙 상 파워셸/쉘 래핑 없이 Python API 직접 호출이 권장됩니다. shell=True 사용은 보안 및 호환성 문제를 야기할 수 있습니다."
                how_desc = "`shell=True`를 없애고 인자를 리스트로 전달하는 방식으로 `subprocess.run`을 호출하도록 수정합니다."
            else:
                title = f"코드 패턴 '{pat}' 개선"
                what_desc = f"코드 내 `{pat}` 패턴의 사용을 제거 또는 개선"
                why_desc = "해당 패턴은 프로젝트 규칙에 어긋나거나 잠재적 문제를 일으킬 수 있습니다."
                how_desc = f"`{pat}` 패턴을 대체할 코드를 적용하고, 필요시 관련 함수를 리팩토링합니다."
            # 제안 섹션 작성
            lines.append(f"### {title}")
            lines.append(f"**WHAT:** {what_desc}합니다. (발견 위치: {', '.join(locations)})")
            lines.append(f"**WHY:** {why_desc}")
            lines.append(f"**HOW:** {how_desc}\n")
    else:
        lines.append("## 코드 규칙 위반 수정 제안\n(금지된 코드 패턴 사용이 발견되지 않았습니다.)\n")

    return "\n".join(lines)

def create_proposal_file(scan_results, output_dir=None):
    """
    스캔 결과를 받아 docs/proposals/auto_update_YYYYMMDD.md 파일을 생성.
    output_dir 지정 시 해당 경로에 파일을 만들고, 미지정시 프로젝트 docs/proposals에 생성.
    반환: 생성된 파일의 Path 객체
    """
    content = generate_proposal_content(scan_results)
    # 파일 이름과 경로 결정
    date_str = datetime.date.today().strftime("%Y%m%d")
    file_name = f"auto_update_{date_str}.md"
    if output_dir:
        proposals_dir = Path(output_dir)
    else:
        # repo 루트/docs/proposals 경로
        proposals_dir = Path(__file__).resolve().parents[2] / "docs" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    file_path = proposals_dir / file_name
    file_path.write_text(content, encoding='utf-8')
    return file_path

if __name__ == "__main__":
    # scanner를 실행하여 바로 제안서 생성까지 수행
    scan_data = scanner.scan_all()
    new_file = create_proposal_file(scan_data)
    print(f"[auto-update] 제안서가 생성되었습니다: {new_file}")
