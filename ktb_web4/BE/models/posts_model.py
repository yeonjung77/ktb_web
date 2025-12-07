from datetime import datetime

# 샘플 게시글
POSTS = [
    {
        "id": 1,
        "title": "2025 패션 공급망의 빅시프트: 중국 탈출, 인도·베트남이 새로운 허브로 뜬다",
        "content": "글로벌 브랜드들이 리스크를 피하기 위해 생산지 다변화를 본격화한다. 아시아 내 재편과 근거리 생산이 경쟁 우위를 결정짓는 요소가 됐다.",
        "image": "/static/image/image1.png",
        "views": 192,
        "comments": 1,
        "likes": 57,
        "created_at": "2025-12-5 15:20:34"
    },
    {
        "id": 2,
        "title": "중국의 그림자 속에서… 인도와 일본, 패션 성장의 새로운 중심으로 부상",
        "content": "중국 소비 둔화와 함께 인도는 폭발적 중산층 성장, 일본은 럭셔리 붐으로 존재감을 키운다. 글로벌 하우스들이 향후 투자를 집중하는 ‘핫스팟’으로 떠오르고 있다.",
        "image": "/static/image/image2.png",
        "views": 9519,
        "comments": 2,
        "likes": 1881,
        "created_at": "2025-12-3 12:10:22"
    },
    {
        "id": 3,
        "title": "재고 문제, 이제는 E2E(End-to-End) 협업 없이는 해결할 수 없다",
        "content": "전통적인 부서별 분리 운영은 재고 손실·품절·데이터 단절을 초래하며 한계에 다다랐다. 브랜드는 기획–소싱–물류–매장까지 연결된 재고 의사결정 체계를 구축해야 비용 10~15% 절감 효과를 얻을 수 있다.",
        "image": "/static/image/image3.png",
        "views": 14789,
        "comments": 2,
        "likes": 3223,
        "created_at": "2025-12-1 10:30:25"
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
    # 최신 게시글이 위로 오도록 역순 정렬
    ordered_posts = list(reversed(POSTS))

    start = (page - 1) * page_size
    end = start + page_size
    sliced = ordered_posts[start:end]

    response = []
    for post in sliced:
        response.append({
            "id": post["id"],
            "title": post["title"],
            "author": post.get("author"),
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
