from BE.models.posts_model import POSTS

def update_post(post_id: int, title: str, content: str, image_filename: str | None):

    post = next((p for p in POSTS if p["id"] == post_id), None)
    if post is None:
        return None

    post["title"] = title
    post["content"] = content

    # 이미지 파일 교체 시
    if image_filename:
        post["image"] = image_filename

    return {
        "success": True,
        "message": "게시글이 수정되었습니다.",
        "post_id": post_id,
        "next_url": f"/posts/{post_id}"
    }
