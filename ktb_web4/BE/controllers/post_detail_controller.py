from fastapi import HTTPException, status
from BE.models.post_detail_model import (
    get_post_detail,
    delete_post,
    toggle_like,
    add_comment,
    update_comment,
    delete_comment
)
from BE.models.comment_model import moderate_comment
from BE.models.signup_model import get_nickname_by_email

# 상세 조회
def post_detail_controller(post_id: int, email: str):
    data = get_post_detail(post_id, email)
    if data is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return data


# 게시글 삭제
def post_delete_controller(post_id: int):
    return delete_post(post_id)


# 좋아요 토글
def post_like_controller(post_id: int, email: str):
    data = toggle_like(post_id, email)
    if data is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return data


# 댓글 등록
def comment_add_controller(
    post_id: int,
    text: str,
    email: str | None = None,
    nickname: str = "",
):
    content = text.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="댓글을 입력해주세요",
        )

    moderation_result = moderate_comment(content)
    if moderation_result["blocked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글이 차단되었습니다",
        )

    # 닉네임 우선 사용, 없으면 이메일 기반 조회
    safe_email = (email or "").strip()
    safe_nickname = (nickname or "").strip()
    display_name = (
        safe_nickname or get_nickname_by_email(safe_email) or safe_email or "손님"
    )

    return add_comment(post_id, content, display_name)


# 댓글 수정
def comment_update_controller(post_id: int, comment_id: int, text: str):
    content = text.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="댓글을 입력해주세요",
        )

    moderation_result = moderate_comment(content)
    if moderation_result["blocked"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글이 차단되었습니다",
        )

    item = update_comment(post_id, comment_id, content)
    if item is None:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")
    return item


# 댓글 삭제
def comment_delete_controller(post_id: int, comment_id: int):
    return delete_comment(post_id, comment_id)
