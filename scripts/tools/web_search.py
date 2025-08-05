from typing import List, Dict
import os
import requests

class ProviderNotConfigured(Exception):
    """Exception raised when a search provider is not configured."""
    pass

def search(query: str, top_k: int = 5) -> List[Dict[str, str]]:
    n = max(1, int(top_k) if top_k else 5)

    if os.getenv("WEB_AGENT_TEST_MODE") == "true":
        base = "https://example.local/dummy"
        return [{"title": f"[DUMMY] {query} - {i+1}",
                 "url": f"{base}?q={i+1}",
                 "snippet": f"{query} 관련 더미 결과 {i+1}"} for i in range(n)]
    
    serper_api_key = os.getenv("SERPER_API_KEY")
    if serper_api_key:
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        payload = json.dumps({"q": query, "num": n})
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
            
            results = []
            for organic_result in data.get('organic', []):
                results.append({
                    "title": organic_result.get('title'),
                    "url": organic_result.get('link'),
                    "snippet": organic_result.get('snippet')
                })
            return results
        except requests.exceptions.RequestException as e:
            print(f"Serper API request failed: {e}", file=sys.stderr)
            raise ProviderNotConfigured("Serper API request failed.") from e
    else:
        raise ProviderNotConfigured("SERPER_API_KEY is not set.")