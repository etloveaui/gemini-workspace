"""
CLI 출력 통일 유틸리티
- 규칙: 단순 텍스트, '===' 구분선, 번호 목록 사용
"""
from typing import Optional


def divider() -> str:
    return "==="


def header(title: str) -> str:
    return f"=== {title} ==="


def section(title: str) -> str:
    return f"=== {title} ==="


def item(index: int, text: str) -> str:
    return f"{index}) {text}"


def kv(key: str, value: object) -> str:
    return f"{key}: {value}"


def status_line(index: int, status: str, name: str, detail: Optional[str] = None) -> str:
    line = f"{index}) [{status}] {name}"
    if detail:
        line += f" - {detail}"
    return line

