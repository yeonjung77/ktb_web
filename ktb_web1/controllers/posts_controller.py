from fastapi import HTTPException
from models.posts_model import get_posts

def posts_list_controller(page: int, page_size: int):
    if page < 1 or page_size < 1:
        raise HTTPException(400, "page와 page_size는 1 이상이어야 합니다.")
    
    return get_posts(page, page_size)