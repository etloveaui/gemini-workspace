from __future__ import annotations

import os
from typing import Optional


def is_enabled() -> bool:
    val = os.getenv("OUTPUT_KO_RATIONALE", "1").strip().lower()
    return val not in {"0", "false", "off", "no"}


def build_rationale(summary_context: str = "", *, hint: Optional[str] = None) -> str:
    """
    한국어 요약 근거를 1–3줄로 생성합니다(비모델, 휴리스틱 설명).
    summary_context: 요약이나 출력의 간단한 컨텍스트 설명(한 줄 권장)
    hint: 'search', 'image', 'generic' 등 선택적 힌트
    """
    lines: list[str] = []
    if hint == "search":
        lines.append("검색 상위 결과 요약 기반 결론.")
        lines.append("키워드 가중치로 핵심 문장만 추출함.")
    elif hint == "image":
        lines.append("이미지 파일명·메타 기반 더미 분석 결과.")
        lines.append("실제 모델 연결 전 임시 동작임.")
    else:
        if summary_context:
            lines.append(summary_context)
        lines.append("입력의 핵심 전제와 제약을 반영한 간단 요약.")

    # 최대 2줄만 반환
    return "\n".join(lines[:2])

