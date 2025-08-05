from typing import List, Dict


def search(query: str, top_k: int = 5) -> List[Dict[str, str]]:
    n = max(1, int(top_k) if top_k else 5)
    base = "https://example.local/dummy"
    return [{"title": f"[DUMMY] {query} - {i+1}",
             "url": f"{base}?q={i+1}",
             "snippet": f"{query} 관련 더미 결과 {i+1}"} for i in range(n)]
