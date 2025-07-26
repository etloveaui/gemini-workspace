# /scripts/build_context_index.py
#
from pathlib import Path
import json
import re
import time
import hashlib

# 워크스페이스 루트 경로를 동적으로 찾음
ROOT = Path(__file__).parent.parent

def get_file_info(file_path: Path):
    """파일의 메타데이터를 추출합니다."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        return {
            "path": str(file_path.relative_to(ROOT)),
            "lines": text.count("\n") + 1,
            "sha1": hashlib.sha1(text.encode("utf-8")).hexdigest(),
            # 간단한 태그 추출 (예: [Project], [System])
            "tags": re.findall(r"\[([A-Za-z\s]+)\]", text)
        }
    except Exception:
        return None

def build_index():
    """워크스페이스의 컨텍스트 인덱스를 생성합니다."""
    print("Building context index...")
    docs = [p for p in ROOT.glob("docs/**/*.md") if p.is_file()]
    
    index_data = {
        "updated_at_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "docs": [info for p in docs if (info := get_file_info(p)) is not None]
    }
    
    output_dir = ROOT / "context"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "index.json"
    
    output_file.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print(f"Context index successfully built at: {output_file}")

if __name__ == "__main__":
    import datetime
    build_index()
