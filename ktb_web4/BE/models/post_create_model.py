from datetime import datetime
from BE.models.posts_model import POSTS
from BE.models.signup_model import get_nickname_by_email


def create_post(
    title: str,
    content: str,
    image_filename: str | None,
    email: str,
    nickname: str = "",
):
    new_id = len(POSTS) + 1

    safe_email = (email or "").strip()
    safe_nickname = (nickname or "").strip()

    # 우선순위: 프론트에서 넘겨준 닉네임 > 가입 정보 조회 > 이메일 > '손님'
    resolved_nickname = (
        safe_nickname or get_nickname_by_email(safe_email) or safe_email or "손님"
    )

    new_post = {
        "id": new_id,
        "title": title,
        "content": content,
        "views": 0,
        "comments": 0,
        "likes": 0,
        "image": image_filename,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "author": resolved_nickname,
    }

    POSTS.append(new_post)

    return {
        "success": True,
        "message": "게시글이 등록되었습니다.",
        "post_id": new_id,
        "next_url": f"/posts/{new_id}",
    }
