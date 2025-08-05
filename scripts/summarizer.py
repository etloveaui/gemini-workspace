# /scripts/summarizer.py
import re

def summarize_text(text: str, max_sentences: int = 5, lang: str = "en") -> str:
    """간단한 추출적 요약(Extractive Summarization)을 수행합니다."""
    # TODO: Implement actual multilingual summarization here based on 'lang'
    # For now, this is a dummy implementation.
    if not text:
        return ""
    
    # 문장 분리 (간단한 방식)
    sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
    if len(sentences) <= max_sentences:
        return text

    # 중요한 키워드 찾기 (예: 'Goal:', 'Error:', '결론:')
    keywords = ['goal', 'error', '결론', '요약', '문제', '해결']
    
    scored_sentences = []
    for sentence in sentences:
        score = 0
        for keyword in keywords:
            if keyword in sentence.lower():
                score += 1
        scored_sentences.append((sentence, score))
        
    # 점수가 높은 순으로 정렬하고, 원래 순서대로 재조합
    top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_sentences]
    
    # 원래 순서대로 다시 정렬하여 요약 생성
    summary_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
    
    return " ".join([s[0] for s in summary_sentences]) + " ... (summarized)"

