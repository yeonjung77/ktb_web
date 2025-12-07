from fastapi import APIRouter, File, UploadFile, Form
from BE.controllers.signup_controller import signup_controller, SignupRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup")
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    password_check: str = Form(...),
    nickname: str = Form(...),
    profile: UploadFile | None = File(None),
):
    """
    회원가입 API
    Form : email, password, password_check, nickname
    File : profile 이미지
    """
    request = SignupRequest(
        email=email,
        password=password,
        password_check=password_check,
        nickname=nickname,
    )
    return await signup_controller(request, profile)
