import logging

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from BE.models.comment_model import moderate_comment

logger = logging.getLogger(__name__)


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

    logger.info(f"Processing comment request: post_id={request.post_id}, content_length={len(content)}")
    
    try:
        moderation_result = moderate_comment(content)
        logger.info(f"Moderation result: {moderation_result}")
        
        if moderation_result["blocked"]:
            logger.warning(f"Comment blocked: '{content[:50]}...'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글이 차단되었습니다",
            )

        logger.info(f"Comment approved: '{content[:50]}...'")
        return {
            "success": True,
            "message": "댓글이 등록되었습니다.",
            "post_id": request.post_id,
            "comment": {"content": content},
            "moderation": moderation_result,
        }
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except Exception as exc:
        # 예상치 못한 예외의 경우 댓글 등록을 차단
        logger.error(f"Unexpected error in comment controller: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 처리 중 오류가 발생했습니다. 댓글은 등록되지 않았습니다.",
        ) from exc
