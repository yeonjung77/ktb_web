from fastapi import APIRouter, Query, Form
from controllers.post_detail_controller import (
    post_detail_controller,
    post_delete_controller,
    post_like_controller,
    comment_add_controller,
    comment_update_controller,
    comment_delete_controller
)

router = APIRouter(
    prefix="/posts",
    tags=["post_detail"]
)

# 상세 조회
@router.get("/{post_id}")
def get_detail(post_id: int, email: str = Query(...)):
    return post_detail_controller(post_id, email)

# 게시글 삭제
@router.delete("/{post_id}")
def delete_post(post_id: int):
    return post_delete_controller(post_id)

# 좋아요 토글
@router.post("/{post_id}/like")
def toggle_like(post_id: int, email: str = Form(...)):
    return post_like_controller(post_id, email)

# 댓글 생성
@router.post("/{post_id}/comments")
def add_comment(post_id: int, text: str = Form(...)):
    return comment_add_controller(post_id, text)

# 댓글 수정
@router.put("/{post_id}/comments/{comment_id}")
def update_comment(post_id: int, comment_id: int, text: str = Form(...)):
    return comment_update_controller(post_id, comment_id, text)

# 댓글 삭제
@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int):
    return comment_delete_controller(post_id, comment_id)