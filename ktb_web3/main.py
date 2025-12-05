from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routes.login_route import router as login_router
from routes.signup_route import router as signup_router
from routes.profile_route import router as profile_router
from routes.password_route import router as password_router
from routes.posts_route import router as posts_router
from routes.post_detail_route import router as post_detail_router
from routes.post_edit_route import router as post_edit_router
from routes.post_create_route import router as post_create_router
from routes.comment_route import router as comment_router

app = FastAPI(
    title="Community Backend",
    description="Route - Controller - Model 패턴 연습용 커뮤니티 백엔드",
    version="1.0.0",
)

# 라우터 등록
app.include_router(login_router)
app.include_router(signup_router)
app.include_router(profile_router)
app.include_router(password_router)
app.include_router(posts_router)
app.include_router(post_detail_router)
app.include_router(post_edit_router)
app.include_router(post_create_router)
app.include_router(comment_router)

# 예상치 못한 모든 에러를 잡는 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
    )
