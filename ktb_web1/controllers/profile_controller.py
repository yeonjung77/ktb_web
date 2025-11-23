import re
from fastapi import HTTPException, UploadFile
from models.signup_model import is_nickname_duplicate
from models.profile_model import update_user, delete_user, get_user

# 닉네임 유효성 검사
def validate_nickname(nickname: str, original_nickname: str):

    if not nickname:
        raise HTTPException(400, "닉네임을 입력해주세요")

    if " " in nickname:
        raise HTTPException(400, "띄어쓰기를 없애주세요")

    if len(nickname) > 10:
        raise HTTPException(400, "닉네임은 최대 10자까지 작성 가능합니다.")

    # 기존 닉네임은 중복 체크 제외
    if nickname != original_nickname and is_nickname_duplicate(nickname):
        raise HTTPException(400, "중복된 닉네임입니다.")


# 프로필 이미지 유효성 검사
async def validate_profile(profile: UploadFile | None):
    if profile is None:
        return None  # 프로필 안 바꿀 수도 있음

    if not profile.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "이미지 파일만 업로드할 수 있습니다.")

    return profile.filename


# 회원정보 수정
async def profile_update_controller(email: str, nickname: str, profile: UploadFile | None):
    user = get_user(email)
    if not user:
        raise HTTPException(400, "유저 정보를 찾을 수 없습니다.")

    # 1) 닉네임 검증
    validate_nickname(nickname, original_nickname=user["nickname"])

    # 2) 프로필 이미지 검증
    profile_filename = await validate_profile(profile)

    # 3) Model에 전달하여 수정 처리
    return update_user(email, nickname, profile_filename)


# 회원탈퇴
def profile_delete_controller(email: str):
    return delete_user(email)
