import json
import logging
import os
import urllib.error
import urllib.request

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

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
    logger.info(f"Moderation response: '{response_text}' (normalized: '{normalized}')")

    # Exact keyword check first
    if normalized.startswith("BLOCK"):
        logger.info("Decision: BLOCK (starts with BLOCK)")
        return True
    if normalized.startswith("ALLOW"):
        logger.info("Decision: ALLOW (starts with ALLOW)")
        return False

    # Fallback: contain check for robustness
    if "BLOCK" in normalized and "ALLOW" not in normalized:
        logger.info("Decision: BLOCK (contains BLOCK without ALLOW)")
        return True
    
    # 명확하지 않은 응답의 경우 안전을 위해 차단 (기본값을 차단으로 변경)
    logger.warning(f"Unclear moderation response: '{response_text}'. Defaulting to BLOCK for safety.")
    return True


def moderate_comment(content: str) -> dict:
    """Check whether a comment should be blocked for profanity or hate speech."""
    logger.info(f"Moderating comment: '{content[:50]}...' (length: {len(content)})")
    
    prompt = (
        "You are a strict Korean content moderation filter for user comments. "
        "You must block comments that contain:\n"
        "- Profanity (욕설): including but not limited to 씨발, 개새끼, 병신, 좆, 시발, 씨발놈, 미친놈, etc.\n"
        "- Hate speech (혐오 발언)\n"
        "- Threats (위협)\n"
        "- Sexual harassment (성적 괴롭힘)\n"
        "- Self-harm encouragement (자해 유도)\n"
        "- Slurs or offensive language (비하 발언)\n"
        "- Creative misspellings or variations of profanity\n\n"
        "If the comment contains ANY of the above, respond with exactly one word: BLOCK\n"
        "If the comment is completely safe and appropriate, respond with exactly one word: ALLOW\n"
        "IMPORTANT: Respond with ONLY one word - either 'BLOCK' or 'ALLOW'. No punctuation, no explanation, no other text.\n\n"
        f"Comment to check: {content}"
    )

    try:
        response_text = _call_ollama(prompt)
        blocked = _should_block(response_text)
        
        logger.info(f"Moderation result for comment '{content[:50]}...': blocked={blocked}, response='{response_text}'")
        
        return {
            "blocked": blocked,
            "decision": response_text,
            "model": MODERATION_MODEL,
            "endpoint": OLLAMA_HOST,
        }
    except HTTPException:
        # HTTPException은 그대로 전파 (이미 적절한 에러 메시지 포함)
        raise
    except Exception as exc:
        # 예상치 못한 예외의 경우 안전을 위해 차단
        logger.error(f"Unexpected error during moderation: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 필터 처리 중 오류가 발생했습니다. 댓글은 차단되었습니다.",
        ) from exc
