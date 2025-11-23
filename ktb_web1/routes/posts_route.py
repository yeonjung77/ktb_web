from fastapi import APIRouter, Query
from controllers.posts_controller import posts_list_controller

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

# 게시글 목록 조회 (무한스크롤)
@router.get("/")
async def get_posts_list(
    page: int = Query(1, description="페이지 번호"),
    page_size: int = Query(10, description="한 페이지 게시글 수")
):
    return posts_list_controller(page, page_size)
