from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SECRET_FILE_PATH = ROOT / "secrets" / "my_sensitive_data.md"

def get_serper_api_key_from_file() -> str | None:
    """my_sensitive_data.md 파일에서 SERPER_API_KEY를 파싱하여 반환합니다."""
    if not SECRET_FILE_PATH.exists():
        return None

    content = SECRET_FILE_PATH.read_text(encoding="utf-8")
    match = re.search(r"### Serper\.dev API Key\n- \*\*용도:\*\* 웹 검색 기능\n- \*\*값:\*\* `([^`]+)`", content)
    if match:
        return match.group(1).strip()
    return None
