import sys
from pathlib import Path
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# scripts.tools.web_search 모듈을 직접 임포트
import scripts.tools.web_search
from scripts.tools.web_search import ProviderNotConfigured
from scripts.summarizer import summarize_text as summarize
from scripts.utils.ko_rationale import is_enabled as _ko_on, build_rationale as _ko_reason

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
        results = scripts.tools.web_search.search(q, top_k=5) # Use the dynamically chosen search function
        if not results:
            print(f"No search results found for '{q}'.")
            sys.exit(0)

        merged = "\n\n".join(r["snippet"] for r in results)
        summary = summarize(merged, max_sentences=5)
        if _ko_on():
            reason = _ko_reason(hint="search")
            print(summary + f"\n\n근거(요약):\n{reason}")
        else:
            print(summary)
    except ProviderNotConfigured as e:
        print(f"Error: Search provider not configured. {e}. Set SERPER_API_KEY or enable WEB_AGENT_TEST_MODE=true.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
