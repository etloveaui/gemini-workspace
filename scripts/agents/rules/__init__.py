import importlib
import pkgutil
from .base import RuleBase

def load_rules(pkg_path=__path__, pkg_name=__name__):
    """지정된 패키지 경로에서 모든 규칙 모듈을 동적으로 임포트합니다."""
    for _, name, _ in pkgutil.iter_modules(pkg_path, prefix=f"{pkg_name}."):
        try:
            importlib.import_module(name)
        except Exception as e:
            print(f"Warning: Could not import rule module '{name}'. Reason: {e}")

def get_rule_names() -> list[str]:
    """등록된 모든 규칙의 이름을 리스트로 반환합니다."""
    return sorted(RuleBase.registry.keys())

def get_rule(name: str) -> type[RuleBase]:
    """이름으로 특정 규칙 클래스를 찾아 반환합니다."""
    if not RuleBase.registry:
        load_rules()
    
    try:
        return RuleBase.registry[name]
    except KeyError:
        available_rules = ", ".join(get_rule_names())
        raise ValueError(f"Unknown rule: '{name}'. Available rules: [{available_rules}]")
