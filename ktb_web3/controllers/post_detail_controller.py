from fastapi import HTTPException
from models.post_detail_model import (
    get_post_detail,
    delete_post,
    toggle_like,
    add_comment,
    update_comment,
    delete_comment
)

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
def comment_add_controller(post_id: int, text: str):
    if not text:
        raise HTTPException(400, "댓글을 입력해주세요")
    return add_comment(post_id, text)


# 댓글 수정
def comment_update_controller(post_id: int, comment_id: int, text: str):
    item = update_comment(post_id, comment_id, text)
    if item is None:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")
    return item


# 댓글 삭제
def comment_delete_controller(post_id: int, comment_id: int):
    return delete_comment(post_id, comment_id)