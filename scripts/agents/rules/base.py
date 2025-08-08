from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Any

class RuleBase(ABC):
    """모든 리팩토링 규칙의 기반이 되는 추상 클래스."""
    registry: ClassVar[Dict[str, type["RuleBase"]]] = {}

    # --- 필수 메타데이터 --- #
    name: ClassVar[str] = ""  # CLI에서 사용될 규칙의 고유 이름
    summary: ClassVar[str] = ""  # 규칙에 대한 한 줄 설명
    params: ClassVar[Dict[str, str]] = {}  # 규칙이 받는 파라미터 스키마 (이름: 설명)
    idempotent: ClassVar[bool] = True  # 규칙이 멱등성을 가지는지 여부
    conflicts: ClassVar[set[str]] = set() # 이 규칙과 충돌하는 다른 규칙 이름들의 집합

    def __init_subclass__(cls, **kwargs):
        """RuleBase를 상속하는 클래스가 정의될 때마다 자동으로 레지스트리에 등록합니다."""
        super().__init_subclass__(**kwargs)
        rule_name = getattr(cls, "name", cls.__name__)
        if not rule_name:
            raise ValueError("Rule must define a non-empty 'name' class variable.")
        if rule_name in RuleBase.registry:
            raise ValueError(f"Rule name '{rule_name}' is already registered.")
        RuleBase.registry[rule_name] = cls

    @abstractmethod
    def apply(self, source: str, **kwargs: Any) -> str:
        """소스 코드를 입력받아 리팩토링을 적용하고, 변경된 소스 코드를 반환합니다."""
        raise NotImplementedError
