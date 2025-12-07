import json
import os
import urllib.error
import urllib.request
from collections import defaultdict
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import HTTPException, status

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()

# 로컬 LLM(Ollama) 설정
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
SOF_LLM_MODEL = os.getenv("SOF_LLM_MODEL", "llama3")


def _call_ollama_chat(messages: List[Dict[str, str]]) -> str:
    """
    Ollama /api/chat 엔드포인트로 요청을 보내는 헬퍼.
    - Ollama 앱이 로컬에서 실행 중이어야 함
    - `ollama pull llama3` 등으로 SOF_LLM_MODEL에 해당하는 모델이 준비되어 있어야 함
    """
    url = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
    payload = {
        "model": SOF_LLM_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1, "top_p": 0.9},
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "패션 리서치용 LLM 서버에 연결할 수 없습니다. "
                "Ollama가 실행 중인지와 SOF_LLM_MODEL에 지정된 모델이 다운로드되어 있는지 확인해주세요."
            ),
        ) from exc
    except Exception as exc:  # pragma: no cover - 방어적 코드
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="패션 리서치용 LLM 호출 중 오류가 발생했습니다.",
        ) from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="패션 리서치용 LLM 응답을 읽을 수 없습니다.",
        ) from exc

    # Ollama /api/chat 응답 형식: { ..., "message": {"role": "assistant", "content": "..."} }
    response_text = parsed.get("message", {}).get("content", "").strip()
    if not response_text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="패션 리서치용 LLM 응답이 비어 있습니다.",
        )

    return response_text


_vectorstore: FAISS | None = None
_bm25_retriever: BM25Retriever | None = None
_by_year_chapter: Dict[Any, Any] | None = None
_by_chapter: Dict[Any, Any] | None = None

CHAPTER_LABELS = ["Global Economy", "Consumer Shifts", "Fashion System"]


def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    base_dir = os.path.dirname(__file__)
    faiss_dir = os.path.join(base_dir, "faiss_index")

    if not os.path.isdir(faiss_dir):
        raise HTTPException(
            status_code=500,
            detail="faiss_index 디렉토리를 찾을 수 없습니다. ktb_web4/faiss_index 를 확인해주세요.",
        )

    _vectorstore = FAISS.load_local(
        faiss_dir, embeddings, allow_dangerous_deserialization=True
    )
    return _vectorstore


def get_bm25_retriever() -> BM25Retriever:
    global _bm25_retriever
    if _bm25_retriever is not None:
      return _bm25_retriever

    vs = get_vectorstore()
    all_docs = list(vs.docstore._dict.values())
    _bm25_retriever = BM25Retriever.from_documents(all_docs, k=50)
    return _bm25_retriever


def get_grouped_docs():
    global _by_year_chapter, _by_chapter
    if _by_year_chapter is not None and _by_chapter is not None:
        return _by_year_chapter, _by_chapter

    vs = get_vectorstore()
    all_docs = list(vs.docstore._dict.values())

    by_year_chapter = defaultdict(list)
    by_chapter = defaultdict(list)

    for d in all_docs:
        year = d.metadata.get("year")
        chapter = d.metadata.get("chapter")
        by_year_chapter[(year, chapter)].append(d)
        by_chapter[chapter].append(d)

    _by_year_chapter, _by_chapter = by_year_chapter, by_chapter
    return _by_year_chapter, _by_chapter


def hybrid_search(
    query: str,
    semantic_k: int = 30,
    keyword_k: int = 30,
    combined_k: int = 12,
    chapter_filter: str | None = None,
    region_filter: str | None = None,
):
    vs = get_vectorstore()
    bm25 = get_bm25_retriever()

    semantic_docs = vs.similarity_search(query, k=semantic_k)
    keyword_docs = bm25.invoke(query)[:keyword_k]

    def make_key(doc):
        return (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.page_content,
        )

    scores: dict = {}
    n_sem = len(semantic_docs) or 1
    n_kw = len(keyword_docs) or 1

    for rank, doc in enumerate(semantic_docs):
        key = make_key(doc)
        sem_score = (n_sem - rank) / n_sem
        prev_sem, prev_kw, prev_doc = scores.get(key, (0.0, 0.0, doc))
        scores[key] = (max(prev_sem, sem_score), prev_kw, doc)

    for rank, doc in enumerate(keyword_docs):
        key = make_key(doc)
        kw_score = (n_kw - rank) / n_kw
        prev_sem, prev_kw, prev_doc = scores.get(key, (0.0, 0.0, doc))
        scores[key] = (prev_sem, max(prev_kw, kw_score), doc)

    alpha = 0.6
    scored_docs = []
    for sem_score, kw_score, doc in scores.values():
        final_score = alpha * sem_score + (1 - alpha) * kw_score

        if chapter_filter and doc.metadata.get("chapter") != chapter_filter:
            continue
        if region_filter and doc.metadata.get("region") != region_filter:
            continue

        scored_docs.append((final_score, doc))

    if not scored_docs:
        scored_docs = [
            (alpha * ((n_sem - i) / n_sem), d) for i, d in enumerate(semantic_docs)
        ]

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored_docs[:combined_k]]


def format_docs(docs) -> str:
    processed = []
    for d in docs:
        src = os.path.basename(d.metadata.get("source", ""))
        page = d.metadata.get("page", "?")
        year = d.metadata.get("year", "")
        chapter = d.metadata.get("chapter", "")
        region = d.metadata.get("region", "")
        if region:
            header = f"[{year} / {chapter} / {region} / {src} p.{page}]"
        else:
            header = f"[{year} / {chapter} / {src} p.{page}]"
        processed.append(header + "\n" + d.page_content)
    return "\n\n".join(processed)


QA_SYSTEM_PROMPT = (
    "You are a professional Fashion MD Research Assistant.\n"
    "Use ONLY the content from McKinsey & BoF 'State of Fashion' (2021–2025).\n"
    "반드시 한국어로만 답변합니다. 문장·단락 전체를 영어로 작성하지 마세요.\n"
    "필요한 핵심 용어(예: 지표 이름, 모델명 등)만 괄호 안에 영어로 병기할 수 있습니다.\n"
    "질문이 영어로 들어와도, 답변은 항상 자연스러운 한국어 문장으로 작성하세요.\n"
    "참고 문서에 명시적으로 없는 수치, 연도, 회사 이름, 세부 사례는 추측해서 만들지 마세요.\n"
    "참고 문서만으로 충분한 근거가 없으면, '해당 내용은 State of Fashion 리포트에서 찾을 수 없습니다.'라고만 답변하세요."
)

REPORT_SYSTEM_PROMPT = (
    "You are a senior fashion strategy consultant.\n"
    "Below is a conversation between a Fashion MD and an AI research assistant\n"
    "about insights from McKinsey & BoF 'State of Fashion' (2021–2025).\n"
    "Use ONLY information that can be reasonably grounded in this conversation.\n"
    "반드시 한국어로만 리포트를 작성합니다. 본문 문장이나 단락을 영어로 작성하지 마세요.\n"
    "필요한 핵심 개념만 괄호 안에 영어로 짧게 병기할 수 있습니다.\n"
    "대화 내용과 명시적으로 연결되지 않는 숫자, 연도, 시장 규모, 구체 사례는 임의로 생성하지 마세요.\n"
    "대화에 정보가 부족하면, '대화 내역만으로는 충분한 인사이트를 도출하기 어렵습니다.'라는 문장을 포함해 한계점을 명시하세요."
)


def answer_question(question: str) -> str:
    if not question.strip():
        raise HTTPException(status_code=400, detail="질문을 입력해주세요.")

    _ = get_vectorstore()

    docs = hybrid_search(
        question,
        semantic_k=30,
        keyword_k=30,
        combined_k=12,
    )

    context = format_docs(docs[:8])
    messages = [
        {
            "role": "system",
            "content": QA_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"질문: {question}\n\n참고 문서:\n{context}",
        },
    ]
    return _call_ollama_chat(messages)


def generate_conversation_report(history: List[Dict[str, str]]) -> str:
    if not history:
        raise HTTPException(
            status_code=400, detail="리포트를 생성할 대화 내용이 없습니다."
        )

    lines = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if not content:
            continue
        role_label = "사용자" if role == "user" else "AI"
        lines.append(f"{role_label}: {content}")

    conversation_text = "\n".join(lines)

    _ = get_vectorstore()

    messages = [
        {
            "role": "system",
            "content": REPORT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "다음은 사용자(패션 MD)와 AI 리서치 어시스턴트의 대화 로그입니다.\n"
                "이 대화를 바탕으로 간결한 인사이트 리포트를 작성해주세요.\n\n"
                f"대화 로그:\n{conversation_text}\n\n"
                "📌 리포트 구성은 다음 섹션을 포함해 주세요.\n"
                "1. Executive Summary\n"
                "2. Key Insights (bullet 형태)\n"
                "3. Implications & Action Ideas (현업 활용 아이디어 중심)\n\n"
                "⚠️ 주의사항\n"
                "- 반드시 대화 내용에서 파생될 수 있는 인사이트만 정리할 것\n"
                "- McKinsey/BoF 리포트에 일반적으로 등장할 법한 문장이라도, 대화에 전혀 나오지 않았다면 생성하지 말 것\n"
                "- 한국어 문장을 사용하되, 필요한 핵심 용어만 영어 병기\n"
                "- 문장은 짧고 명료하게, 실제 보고서에 바로 붙여 넣을 수 있는 톤으로 작성"
            ),
        },
    ]

    return _call_ollama_chat(messages)
