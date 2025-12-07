import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from BE.routes.login_route import router as login_router
from BE.routes.signup_route import router as signup_router
from BE.routes.profile_route import router as profile_router
from BE.routes.password_route import router as password_router
from BE.routes.posts_route import router as posts_router
from BE.routes.post_detail_route import router as post_detail_router
from BE.routes.post_edit_route import router as post_edit_router
from BE.routes.post_create_route import router as post_create_router
from BE.routes.comment_route import router as comment_router
from BE.routes.chat_report_route import router as chat_report_router

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "FE", "static")

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
app.include_router(chat_report_router)

# 정적 파일 (바닐라 JS 프론트엔드) 서빙
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """
    과제 4용 프론트엔드 페이지
    - 브라우저에서 http://localhost:8000/ 접속
    - 바닐라 JS로 백엔드의 /comments 엔드포인트를 호출
    """
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)

# 예상치 못한 모든 에러를 잡는 전역 예외 처리
# HTTPException은 FastAPI가 자동으로 처리하므로 제외
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # HTTPException은 FastAPI가 자동으로 처리하므로 여기서는 처리하지 않음
    if isinstance(exc, HTTPException):
        raise exc
    
    # 예상치 못한 예외만 여기서 처리
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
    )
