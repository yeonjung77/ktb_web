from fastapi import APIRouter

from controllers.comment_controller import CommentRequest, create_comment_controller

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/")
async def create_comment(request: CommentRequest):
    """
    댓글 작성 엔드포인트
    - POST /comments
    - Body: { "content": "댓글 내용", "post_id": 1 (optional) }
    """
    return create_comment_controller(request)
