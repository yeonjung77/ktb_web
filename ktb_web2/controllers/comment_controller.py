from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from models.comment_model import moderate_comment


class CommentRequest(BaseModel):
    post_id: int | None = Field(
        default=None,
        description="댓글을 달 게시글 ID (선택사항)",
    )
    content: str = Field(..., description="댓글 내용")


def create_comment_controller(request: CommentRequest) -> dict:
    content = request.content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="댓글 내용을 입력해주세요.",
        )

    moderation_result = moderate_comment(content)
    if moderation_result["blocked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글이 차단되었습니다",
        )

    return {
        "success": True,
        "message": "댓글이 등록되었습니다.",
        "post_id": request.post_id,
        "comment": {"content": content},
        "moderation": moderation_result,
    }
