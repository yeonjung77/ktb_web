from datetime import datetime
from models.posts_model import POSTS

def create_post(title: str, content: str, image_filename: str | None, email: str):

    new_id = len(POSTS) + 1

    new_post = {
        "id": new_id,
        "title": title,
        "content": content,
        "views": 0,
        "comments": 0,
        "likes": 0,
        "image": image_filename,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "author": email
    }

    POSTS.append(new_post)

    return {
        "success": True,
        "message": "게시글이 등록되었습니다.",
        "post_id": new_id,
        "next_url": f"/posts/{new_id}"
    }