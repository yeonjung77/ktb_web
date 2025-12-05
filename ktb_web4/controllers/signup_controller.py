import re
from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel
from models.signup_model import (
    is_email_duplicate,
    is_nickname_duplicate,
    save_user,
)


class SignupRequest(BaseModel):
    email: str
    password: str
    password_check: str
    nickname: str


# ----------------------------
# 이메일 검사
# ----------------------------
def validate_email(email: str):
    if not email:
        raise HTTPException(400, "이메일을 입력해주세요")

    # 영문/숫자 + @ + . 만 허용
    if not re.match(r"^[A-Za-z0-9@.]+$", email):
        raise HTTPException(400, "올바른 이메일 주소 형식을 입력해주세요(예 : example@example.com)")

    # 형식 검사
    if len(email) < 6 or "@" not in email or "." not in email:
        raise HTTPException(400, "올바른 이메일 주소 형식을 입력해주세요(예 : example@example.com)")

    # 중복 검사
    if is_email_duplicate(email):
        raise HTTPException(400, "중복된 이메일입니다.")


# ----------------------------
# 비밀번호 검사
# ----------------------------
def validate_password(password: str, password_check: str):

    if not password:
        raise HTTPException(400, "비밀번호를 입력해주세요")

    if not password_check:
        raise HTTPException(400, "비밀번호를 한번 더 입력해주세요")

    # 규칙: 8~20자, 대문자/소문자/숫자/특수문자 포함
    cond = (
        len(password) < 8 or len(password) > 20 or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[a-z]", password) or
        not re.search(r"[0-9]", password) or
        not re.search(r"[^A-Za-z0-9]", password)
    )

    if cond:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
        )

    # 비밀번호 확인 불일치
    if password != password_check:
        raise HTTPException(400, "비밀번호가 다릅니다")


# ----------------------------
# 닉네임 검사
# ----------------------------
def validate_nickname(nickname: str):
    if not nickname:
        raise HTTPException(400, "닉네임을 입력해주세요")

    if " " in nickname:
        raise HTTPException(400, "띄어쓰기를 없애주세요")

    if len(nickname) > 10:
        raise HTTPException(400, "닉네임은 최대 10자까지 작성 가능합니다.")

    if is_nickname_duplicate(nickname):
        raise HTTPException(400, "중복된 닉네임입니다.")


# ----------------------------
# 프로필 이미지 검사
# ----------------------------
async def validate_profile(profile_image: UploadFile | None):
    if profile_image is None:
        raise HTTPException(400, "프로필 사진을 추가해주세요")

    # 확장자 검사
    if not profile_image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "이미지 파일만 업로드할 수 있습니다.")

    return profile_image.filename


# ----------------------------
# 회원가입 controller
# ----------------------------
async def signup_controller(request: SignupRequest, profile: UploadFile | None):
    email = request.email
    password = request.password
    password_check = request.password_check
    nickname = request.nickname

    # 입력값 검증
    validate_email(email)
    validate_password(password, password_check)
    validate_nickname(nickname)

    # 프로필 이미지 검증
    profile_filename = await validate_profile(profile)

    # 저장
    result = save_user(email, password, nickname, profile_filename)

    return result
