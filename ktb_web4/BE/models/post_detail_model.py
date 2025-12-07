from datetime import datetime
from BE.models.posts_model import POSTS, format_count

# 댓글 데이터 저장소
COMMENTS = {
    1: [
        {"id": 1, "text": "첫 번째 댓글입니다", "created_at": "2025-12-05 17:57:54", "author": "관리자"},
        {"id": 2, "text": "두 번째 댓글입니다", "created_at": "2025-12-06 08:11:19", "author": "관리자"},
    ],
    2: [],
    3: []
}

# 게시글 좋아요 상태 저장 (email 별 좋아요 판별)
POST_LIKES = {
    # post_id: {email: True/False}
    1: {},
    2: {},
    3: {},
}

# ---------------------------
# 상세 조회 + 조회수 증가
# ---------------------------
def get_post_detail(post_id: int, email: str):

    post = next((p for p in POSTS if p["id"] == post_id), None)
    if post is None:
        return None

    # 조회수 증가
    post["views"] += 1

    # 좋아요 상태
    liked = POST_LIKES.get(post_id, {}).get(email, False)

    # 댓글 목록 가져오기
    comments = COMMENTS.get(post_id, [])

    detail = {
        "id": post["id"],
        "title": post["title"],
        "content": post["content"],
        "image": post.get("image"),
        "views": format_count(post["views"]),
        "likes": format_count(post["likes"]),
        "comments_count": format_count(len(comments)),
        "liked": liked,
        "created_at": post["created_at"],
        "author": post.get("author"),
        "comments": comments,
    }

    return detail


# ---------------------------
# 게시글 삭제
# ---------------------------
def delete_post(post_id: int):
    # models.posts_model.POSTS 를 직접 수정해야
    # 목록 조회(get_posts)에서도 삭제 결과가 반영됨.
    POSTS[:] = [p for p in POSTS if p["id"] != post_id]
    COMMENTS.pop(post_id, None)
    POST_LIKES.pop(post_id, None)
    return {"success": True, "message": "게시글이 삭제되었습니다."}


# ---------------------------
# 좋아요 토글
# ---------------------------
def toggle_like(post_id: int, email: str):
    if post_id not in POST_LIKES:
        POST_LIKES[post_id] = {}

    current = POST_LIKES[post_id].get(email, False)

    # 현재 좋아요 상태 반대로 변경
    POST_LIKES[post_id][email] = not current

    # 좋아요 수 증가/감소
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return None

    if current:
        post["likes"] -= 1
    else:
        post["likes"] += 1

    return {
        "success": True,
        "liked": not current,
        "likes": format_count(post["likes"])
    }


# ---------------------------
# 댓글 생성
# ---------------------------
def add_comment(post_id: int, text: str, author: str):
    new_id = len(COMMENTS.get(post_id, [])) + 1
    comment = {
        "id": new_id,
        "text": text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "author": author,
    }

    COMMENTS.setdefault(post_id, []).append(comment)

    return comment


# ---------------------------
# 댓글 수정
# ---------------------------
def update_comment(post_id: int, comment_id: int, text: str):

    post_comments = COMMENTS.get(post_id, [])
    for c in post_comments:
        if c["id"] == comment_id:
            c["text"] = text
            return c

    return None


# ---------------------------
# 댓글 삭제
# ---------------------------
def delete_comment(post_id: int, comment_id: int):

    COMMENTS[post_id] = [
        c for c in COMMENTS[post_id] if c["id"] != comment_id
    ]

    return {"success": True, "message": "댓글이 삭제되었습니다."}
