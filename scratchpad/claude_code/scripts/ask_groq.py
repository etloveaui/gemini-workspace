# ask_groq.py
# -*- coding: utf-8 -*-
# Usage:
#   python ask_groq.py "질문"
#   python ask_groq.py --route think "깊은 추론"
#   python ask_groq.py --route code  "리팩터링 포인트 찾아줘"
#   echo "stdin" | python ask_groq.py -r fast
import os, sys, json, re, argparse, urllib.request, urllib.error, time

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 모델 라우팅 (Kimi 기본) ---
KIMI = "moonshotai/kimi-k2-instruct"
LLAMA70 = "llama-3.3-70b-versatile"
QWEN32 = "qwen/qwen3-32b"
LLAMA8 = "llama-3.1-8b-instant"
GEMMA9 = "gemma2-9b-it"

DEFAULT_ROUTE = "default"
ROUTE_PRIMARY = {
    "think": [KIMI, LLAMA70],        # 고정밀 추론
    "code":  [QWEN32, LLAMA70],      # 코드·툴
    "long":  [LLAMA70, KIMI],        # 장문 맥락
    "fast":  [LLAMA8, GEMMA9],       # 저지연
    DEFAULT_ROUTE: [KIMI, LLAMA70],  # 기본
}
ROUTE_TEMP = {"think":0.2, "code":0.1, "long":0.3, "fast":0.5, DEFAULT_ROUTE:0.3}

def read_all_stdin() -> str:
    if sys.stdin and not sys.stdin.isatty():
        data = sys.stdin.read()
        if data:
            return data.strip()
    return ""

def load_groq_key_from_secrets() -> str:
    """Prefer environment variable, fallback to local secrets file."""
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    base = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(base, "secrets", "my_sensitive_data.md")
    if not os.path.isfile(secrets_path):
        raise SystemExit("GROQ_API_KEY 미설정: 환경변수 GROQ_API_KEY 또는 secrets/my_sensitive_data.md(gsk_...) 필요")
    txt = open(secrets_path, "r", encoding="utf-8", errors="ignore").read()
    m = re.search(r"(gsk_[A-Za-z0-9_-]+)", txt)
    if not m:
        raise SystemExit("GROQ 키를 찾지 못함: secrets/my_sensitive_data.md 내 gsk_ 패턴 미검출")
    return m.group(1)

def call_groq(api_key: str, prompt: str, model: str, temperature: float, max_tokens: int | None = None, timeout: float = 90.0):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(temperature),
    }
    if max_tokens is not None:
        payload["max_tokens"] = int(max_tokens)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "claude-router/0.1 (+groq)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def try_with_fallbacks(api_key: str, prompt: str, models: list[str], temperature: float, max_tokens: int | None = None, timeout: float = 90.0):
    last_err = None
    for i, m in enumerate(models):
        try:
            return call_groq(api_key, prompt, m, temperature, max_tokens=max_tokens, timeout=timeout), m
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code} {m}: {body}"
            # 429 대기 후 다음 모델 시도
            if e.code == 429:
                ra = e.headers.get("retry-after")
                if ra:
                    try:
                        time.sleep(min(5, float(ra)))
                    except:  # noqa
                        time.sleep(2)
                # 다음 모델로 폴백
                continue
            # 404/400 등은 바로 폴백
            if e.code in (400, 404):
                continue
        except Exception as ex:
            last_err = f"{type(ex).__name__} {m}: {ex}"
            continue
    raise SystemExit(last_err or "모든 모델 시도 실패")

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("prompt", nargs="*")
    ap.add_argument("-r", "--route", choices=["think", "code", "long", "fast"])
    ap.add_argument("-m", "--model", help="모델 직접 지정 시 라우팅 무시")
    ap.add_argument("-t", "--temperature", type=float, help="기본 라우팅 온도 덮어쓰기")
    ap.add_argument("--json", action="store_true", help="원시 JSON 출력")
    ap.add_argument("--max-tokens", type=int, default=None, help="응답 토큰 상한(기본: 공급자 기본값)")
    ap.add_argument("--timeout", type=float, default=90.0, help="요청 타임아웃 초")
    ap.add_argument("--show-model", action="store_true", help="선택 모델을 stderr에 표시")
    args = ap.parse_args()

    prompt = read_all_stdin() or " ".join(args.prompt).strip()
    if not prompt:
        prompt = "간단히 자기소개"

    api_key = load_groq_key_from_secrets()

    route = args.route or DEFAULT_ROUTE
    models = [args.model] if args.model else ROUTE_PRIMARY.get(route, ROUTE_PRIMARY[DEFAULT_ROUTE])
    temp = args.temperature if args.temperature is not None else ROUTE_TEMP.get(route, ROUTE_TEMP[DEFAULT_ROUTE])

    resp, used_model = try_with_fallbacks(api_key, prompt, models, temp, max_tokens=args.max_tokens, timeout=float(args.timeout))
    if args.show_model:
        sys.stderr.write(f"[model] {used_model}\n")

    if args.json:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        return

    try:
        print(resp["choices"][0]["message"]["content"].strip())
    except Exception:
        print(json.dumps(resp, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
