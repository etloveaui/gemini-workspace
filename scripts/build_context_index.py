# /scripts/build_context_index.py
#
from pathlib import Path
import json
import re
import time
import hashlib
import datetime

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
    output_dir = ROOT / "context"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "index.json"

    current_file_hashes = {}
    docs = [p for p in ROOT.glob("docs/**/*.md") if p.is_file()]
    for p in docs:
        info = get_file_info(p)
        if info:
            current_file_hashes[info["path"]] = info["sha1"]

    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_index_data = json.load(f)
            
            # 기존 인덱스의 파일 해시와 현재 파일 해시를 비교
            index_changed = False
            for doc in existing_index_data.get("docs", []):
                path = doc["path"]
                sha1 = doc["sha1"]
                if current_file_hashes.get(path) != sha1:
                    index_changed = True
                    break
            
            if not index_changed and len(existing_index_data.get("docs", [])) == len(docs):
                print("Context index is up to date. No rebuild needed.")
                return
        except json.JSONDecodeError:
            print("Existing index file is corrupted. Rebuilding...")

    index_data = {
        "updated_at_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "docs": [info for p in docs if (info := get_file_info(p)) is not None]
    }
    
    output_file.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print("Context index built successfully.")

if __name__ == "__main__":
    build_index()