# /scripts/prompt_builder.py (재구축 버전)
import yaml
from pathlib import Path
from context_store import ContextStore
from summarizer import summarize_text
import sys

ROOT = Path(__file__).parent.parent
POLICY_PATH = ROOT / ".gemini" / "context_policy.yaml"

def build_prompt_context(policy_name: str) -> str:
    """정책, 리트리버, 요약기를 사용하여 최종 프롬프트 컨텍스트를 합성합니다."""
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"Policy file not found at {POLICY_PATH}")

    with POLICY_PATH.open('r', encoding='utf-8') as f:
        policy = yaml.safe_load(f)

    if policy_name not in policy:
        raise ValueError(f"Policy '{policy_name}' not found in {POLICY_PATH}")

    target_policy = policy[policy_name]
    store = ContextStore()
    final_context_parts = [f"# Context for: {policy_name} (Assembled by Engine)\n"]
    
    total_tokens = 0
    max_tokens = target_policy.get("max_tokens", 1500)

    for source in target_policy.get("sources", []):
        if "doc_tag" in source:
            query = source["doc_tag"]
            retrieved_docs = store.retrieve(query)
            
            for doc in retrieved_docs:
                content = doc['content']
                content_tokens = len(content.split())

                if total_tokens + content_tokens > max_tokens:
                    # 토큰이 넘치면 요약을 시도
                    summary = summarize_text(content)
                    summary_tokens = len(summary.split())
                    if total_tokens + summary_tokens <= max_tokens:
                        final_context_parts.append(f"## Content from: {doc['path']}\n{summary}\n")
                        total_tokens += summary_tokens
                    continue # 요약해도 넘치면 그냥 건너뜀

                final_context_parts.append(f"## Content from: {doc['path']}\n{content}\n")
                total_tokens += content_tokens

    return "\n".join(final_context_parts)

if __name__ == "__main__":
    policy_name_arg = sys.argv[1] if len(sys.argv) > 1 else "session_start_briefing"
    context_result = build_prompt_context(policy_name_arg)
    sys.stdout.buffer.write(context_result.encode('utf-8', errors='ignore'))
    sys.stdout.flush()