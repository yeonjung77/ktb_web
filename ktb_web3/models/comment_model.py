import json
import os
import urllib.error
import urllib.request

from fastapi import HTTPException, status

# Allow override so different models/endpoints can be tested without code changes.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODERATION_MODEL = os.getenv("OLLAMA_MODERATION_MODEL", "llama3")


def _call_ollama(prompt: str) -> str:
    """Send a single non-streaming generation request to Ollama."""
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": MODERATION_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "top_p": 0.1},
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 필터 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요.",
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 필터 처리 중 오류가 발생했습니다.",
        ) from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 필터 응답을 읽을 수 없습니다.",
        ) from exc

    response_text = parsed.get("response", "").strip()
    if not response_text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 필터 응답이 비어 있습니다.",
        )

    return response_text


def _should_block(response_text: str) -> bool:
    """
    Parse the model response.

    The prompt enforces a single word: ALLOW or BLOCK.
    This parser still tolerates minor deviations (e.g., "BLOCK." or explanations).
    """
    normalized = response_text.strip().upper()

    # Exact keyword check first
    if normalized.startswith("BLOCK"):
        return True
    if normalized.startswith("ALLOW"):
        return False

    # Fallback: contain check for robustness
    return "BLOCK" in normalized and "ALLOW" not in normalized


def moderate_comment(content: str) -> dict:
    """Check whether a comment should be blocked for profanity or hate speech."""
    prompt = (
        "You are a strict Korean content moderation filter for user comments. "
        "If the comment contains profanity, hate speech, threats, sexual harassment, "
        "self-harm encouragement, or slurs (including creative misspellings), respond with exactly one word: BLOCK. "
        "If it is safe, respond with exactly one word: ALLOW. "
        "No punctuation, no explanation."
        f"\n\nComment: {content}"
    )

    response_text = _call_ollama(prompt)
    blocked = _should_block(response_text)

    return {
        "blocked": blocked,
        "decision": response_text,
        "model": MODERATION_MODEL,
        "endpoint": OLLAMA_HOST,
    }
