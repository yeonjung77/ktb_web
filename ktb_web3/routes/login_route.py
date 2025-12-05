from fastapi import APIRouter
from controllers.login_controller import login_controller, LoginRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
async def login(request: LoginRequest):
    """
    로그인 엔드포인트
    - POST /auth/login
    - Body: { "email": "...", "password": "..." }
    """
    return login_controller(request)
