from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from BE.sof_langchain import answer_question, generate_conversation_report


router = APIRouter(prefix="/chat_report", tags=["chat_report"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


class ChatTurn(BaseModel):
    role: str
    content: str


class ReportRequest(BaseModel):
    history: List[ChatTurn]


class ReportResponse(BaseModel):
    report: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = answer_question(req.question)
    return ChatResponse(answer=answer)


@router.post("/report", response_model=ReportResponse)
async def report(req: ReportRequest):
    report_text = generate_conversation_report(
        [{"role": t.role, "content": t.content} for t in req.history]
    )
    return ReportResponse(report=report_text)
