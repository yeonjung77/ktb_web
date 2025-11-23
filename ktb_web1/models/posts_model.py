from datetime import datetime

# 3개 샘플 게시글 (DB 대신 임시 데이터)
POSTS = [
    {
        "id": 1,
        "title": "제목입니다 첫번째 게시글",
        "content": "내용1",
        "views": 1200,
        "comments": 23,
        "likes": 41,
        "created_at": "2025-01-10 03:20:30"
    },
    {
        "id": 2,
        "title": "두번째 게시글입니다",
        "content": "내용2",
        "views": 980,
        "comments": 11,
        "likes": 52,
        "created_at": "2025-01-09 12:10:20"
    },
    {
        "id": 3,
        "title": "세번째 게시글",
        "content": "내용3",
        "views": 21000,
        "comments": 188,
        "likes": 3020,
        "created_at": "2025-01-08 08:30:00"
    }
]


def format_count(num: int):
    """1k, 10k, 100k 단위 포맷"""
    if num >= 100000:
        return "100k"
    elif num >= 10000:
        return "10k"
    elif num >= 1000:
        return "1k"
    return str(num)


def get_posts(page: int, page_size: int):
    """무한스크롤용 페이지네이션"""
    start = (page - 1) * page_size
    end = start + page_size
    sliced = POSTS[start:end]

    response = []
    for post in sliced:
        response.append({
            "id": post["id"],
            "title": post["title"],
            "views": format_count(post["views"]),
            "comments": format_count(post["comments"]),
            "likes": format_count(post["likes"]),
            "created_at": post["created_at"]
        })

    return {
        "success": True,
        "page": page,
        "page_size": page_size,
        "posts": response,
        "total": len(POSTS)
    }