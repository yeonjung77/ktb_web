from fastapi import APIRouter, File, UploadFile, Depends
from controllers.signup_controller import signup_controller, SignupRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup")
async def signup(request: SignupRequest, profile: UploadFile | None = File(None)):
    """
    회원가입 API
    Body : email, password, password_check, nickname
    File : profile 이미지
    """
    return await signup_controller(request, profile)