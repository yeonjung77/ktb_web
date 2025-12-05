import os
from collections import defaultdict
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import HTTPException

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()
_groq_key = os.getenv("GROQ_API_KEY")


def _ensure_groq_key():
    if not _groq_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY가 설정되지 않았습니다. 서버 .env에 GROQ_API_KEY를 추가해주세요.",
        )


_vectorstore: FAISS | None = None
_bm25_retriever: BM25Retriever | None = None
_llm: ChatGroq | None = None
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


def get_llm() -> ChatGroq:
    global _llm
    if _llm is not None:
        return _llm

    _ensure_groq_key()
    _llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=_groq_key,
    )
    return _llm


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


qa_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a professional Fashion MD Research Assistant.\n"
            "Use ONLY the content from McKinsey & BoF 'State of Fashion' (2021–2025).\n"
            "답변은 한국어로, 핵심 용어는 영어 병기해줘.",
        ),
        (
            "human",
            "질문: {question}\n\n"
            "참고 문서:\n{context}",
        ),
    ]
)

report_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior fashion strategy consultant.\n"
            "Below is a conversation between a Fashion MD and an AI research assistant\n"
            "about insights from McKinsey & BoF 'State of Fashion' (2021–2025).\n"
            "Use ONLY information that can be reasonably grounded in this conversation.\n"
            "답변은 한국어로 작성하고, 핵심 개념은 필요할 때만 영어 병기해줘.",
        ),
        (
            "human",
            "다음은 사용자(패션 MD)와 AI 리서치 어시스턴트의 대화 로그입니다.\n"
            "이 대화를 바탕으로 간결한 인사이트 리포트를 작성해주세요.\n\n"
            "대화 로그:\n{conversation}\n\n"
            "📌 리포트 구성은 다음 섹션을 포함해 주세요.\n"
            "1. Executive Summary\n"
            "2. Key Insights (bullet 형태)\n"
            "3. Implications & Action Ideas (현업 활용 아이디어 중심)\n\n"
            "⚠️ 주의사항\n"
            "- 반드시 대화 내용에서 파생될 수 있는 인사이트만 정리할 것\n"
            "- McKinsey/BoF 리포트에 일반적으로 등장할 법한 문장이라도, 대화에 전혀 나오지 않았다면 생성하지 말 것\n"
            "- 한국어 문장을 사용하되, 필요한 핵심 용어만 영어 병기\n"
            "- 문장은 짧고 명료하게, 실제 보고서에 바로 붙여 넣을 수 있는 톤으로 작성",
        ),
    ]
)


def answer_question(question: str) -> str:
    if not question.strip():
        raise HTTPException(status_code=400, detail="질문을 입력해주세요.")

    _ = get_vectorstore()
    _ = get_llm()

    docs = hybrid_search(
        question,
        semantic_k=30,
        keyword_k=30,
        combined_k=12,
    )

    context = format_docs(docs[:8])
    chain = qa_prompt | get_llm() | StrOutputParser()
    return chain.invoke({"question": question, "context": context})


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
    _ = get_llm()

    chain = report_prompt | get_llm() | StrOutputParser()
    return chain.invoke({"conversation": conversation_text})

