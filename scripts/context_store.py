import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "context" / "index.json"

class ContextStore:
    def __init__(self):
        self.index = self._load_index()

    def _load_index(self):
        if not INDEX_PATH.exists():
            return {"docs": []}
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def retrieve(self, query: dict):
        """쿼리에 해당하는 문서를 검색합니다. 현재는 태그 또는 경로를 지원합니다."""
        matching_docs = []
        for doc in self.index.get("docs", []):
            # 태그 검색
            if "doc_tag" in query and query["doc_tag"] in doc.get("tags", []):
                matching_docs.append(doc)
            # 경로 검색 (정규식)
            elif "file_path" in query and re.search(query["file_path"], doc.get("path", "")):
                matching_docs.append(doc)
            # 기타 쿼리 (예: 전체 문서)
            elif query.get("all"): # query가 {"all": True}일 경우
                matching_docs.append(doc)
        return matching_docs

    def get_context_by_tag(self, tag: str):
        """태그에 해당하는 컨텍스트를 반환합니다."""
        return [doc for doc in self.index.get("docs", []) if tag in doc.get("tags", [])]

    def get_context_by_path(self, path: str):
        """경로에 해당하는 컨텍스트를 반환합니다."""
        return [doc for doc in self.index.get("docs", []) if re.search(path, doc.get("path", ""))]

    def get_all_context(self):
        """모든 컨텍스트를 반환합니다."""
        return self.index.get("docs", [])

if __name__ == "__main__":
    import sys

    store = ContextStore()

    if len(sys.argv) > 1:
        query_type = sys.argv[1]
        query_value = sys.argv[2]

        if query_type == "tag":
            results = store.get_context_by_tag(query_value)
        elif query_type == "path":
            results = store.get_context_by_path(query_value)
        else:
            results = []

        print(json.dumps(results, indent=2))
    else:
        print(json.dumps(store.get_all_context(), indent=2))