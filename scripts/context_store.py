# /scripts/context_store.py (업그레이드 버전)
import json
from pathlib import Path
from rank_bm25 import BM25Okapi
import subprocess
import datetime

ROOT = Path(__file__).parent.parent
INDEX_PATH = ROOT / "context" / "index.json"

class ContextStore:
    def __init__(self):
        self.index_data = self._load_index()
        self.documents = self.index_data.get("docs", [])
        # BM25 모델을 위한 말뭉치(corpus) 준비
        self.corpus = [self._get_document_text(doc['path']) for doc in self.documents]
        self.tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def _load_index(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"Index not found. Run 'invoke build-context-index'.")
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    def _get_document_text(self, relative_path):
        full_path = ROOT / relative_path
        return full_path.read_text(encoding='utf-8', errors='replace') if full_path.exists() else ""

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """BM25 알고리즘과 추가 가중치를 사용해 관련 문서를 검색하고 스코어링합니다."""
        tokenized_query = query.lower().split()
        doc_scores = self.bm25.get_scores(tokenized_query)

        scored_docs = []
        for i, doc in enumerate(self.documents):
            score = doc_scores[i]
            
            # 추가 가중치: HUB.md는 항상 중요
            if "hub.md" in doc['path'].lower():
                score *= 1.5 
            
            # 최신성 가중치 추가 (git log 활용)
            try:
                cmd = ["git", "log", "-1", "--pretty=format:%ct", "--", str(ROOT / doc['path'])]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=ROOT)
                timestamp = int(result.stdout.strip())
                age_seconds = (datetime.datetime.now().timestamp() - timestamp)
                # 1주일 이내 파일에 가중치 부여 (예시)
                if age_seconds < 7 * 24 * 3600:
                    score *= 1.2
            except Exception:
                pass # git log 실패 시 무시

            if score > 0.1: # 최소 점수 임계값
                # 콘텐츠 스니펫 추출
                content = self.corpus[i]
                snippet = self._extract_snippet(content, tokenized_query)

                scored_docs.append({
                    "path": doc["path"],
                    "score": score,
                    "content": snippet # 스니펫 반환
                })

        return sorted(scored_docs, key=lambda x: x["score"], reverse=True)[:top_k]

    def _extract_snippet(self, text: str, query_tokens: list, snippet_length: int = 50) -> str:
        """쿼리 토큰을 포함하는 문단을 찾아 스니펫을 반환합니다."""
        sentences = text.split('.') # 간단한 문장 분리
        for sentence in sentences:
            if any(token in sentence.lower() for token in query_tokens):
                # 쿼리 토큰이 포함된 문장 주변을 스니펫으로 반환
                start_index = max(0, text.lower().find(query_tokens[0]) - snippet_length // 2)
                end_index = min(len(text), start_index + snippet_length)
                return text[start_index:end_index] + "..."
        return text[:snippet_length] + "..." # 쿼리 토큰이 없으면 앞부분 반환

if __name__ == "__main__":
    import sys
    # 스크립트 직접 실행 테스트용
    store = ContextStore()
    search_query = "active tasks" if len(sys.argv) < 2 else sys.argv[1]
    results = store.retrieve(search_query)
    print(json.dumps(results, indent=2))