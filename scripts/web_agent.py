import sys
from pathlib import Path
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# scripts.tools.web_search 모듈을 직접 임포트
import scripts.tools.web_search
from scripts.summarizer import summarize_text as summarize

# Check for test mode environment variable
if os.environ.get("WEB_AGENT_TEST_MODE") == "true":
    # In test mode, define a mock search function
    def mock_search(query, top_k=5):
        # This DUMMY_RESULTS should ideally come from the test,
        # but for simplicity, we'll hardcode it here for now.
        # A more robust solution would involve passing mock data via env vars or a temp file.
        return [
            {"title": "Mock Python", "url": "https://mock.python.org", "snippet": "Mock Python official website."},
            {"title": "Mock Docs", "url": "https://mock.docs.python.org", "snippet": "Mock Documentation for Python."},
        ]
    search_function = mock_search
else:
    search_function = scripts.tools.web_search.search

def _parse_args(args):
    query = ""
    for i, arg in enumerate(args):
        if arg == "--query" and i + 1 < len(args):
            query = args[i+1]
            break
    return query

def main():
    sys.stdout.reconfigure(encoding='utf-8') # Ensure UTF-8 output
    q = _parse_args(sys.argv)
    if not q:
        print("Error: --query argument is required.")
        sys.exit(1)

    try:
        results = search_function(q, top_k=5) # Use the dynamically chosen search function
        if not results:
            print(f"No search results found for '{q}'.")
            sys.exit(0)

        merged = "\n\n".join(r["snippet"] for r in results)
        summary = summarize(merged, max_sentences=5)
        print(summary)
    except NotImplementedError:
        print("Error: Web search functionality is not yet implemented.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


