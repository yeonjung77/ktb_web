from fastapi import APIRouter, UploadFile, File, Form
from controllers.profile_controller import (
    profile_update_controller,
    profile_delete_controller
)

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

# 회원정보 수정
@router.put("/update")
async def update_profile(
    email: str = Form(...),
    nickname: str = Form(...),
    profile: UploadFile | None = File(None)
):
    return await profile_update_controller(email, nickname, profile)


# 회원탈퇴
@router.delete("/delete")
async def delete_account(email: str = Form(...)):
    return profile_delete_controller(email)