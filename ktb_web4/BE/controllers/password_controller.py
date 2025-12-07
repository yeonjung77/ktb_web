import re
from fastapi import HTTPException
from BE.models.password_model import update_password

def validate_password(password: str, password_check: str):

    # 비밀번호 입력 안 함
    if not password:
        raise HTTPException(400, "비밀번호를 입력해주세요")

    # 비밀번호 확인 입력 안 함
    if not password_check:
        raise HTTPException(400, "비밀번호를 한번 더 입력해주세요")

    # 유효성 조건
    cond = (
        len(password) < 8 or len(password) > 20 or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[a-z]", password) or
        not re.search(r"[0-9]", password) or
        not re.search(r"[^\w]", password)
    )

    if cond:
        raise HTTPException(
            400,
            "비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
        )

    # 비밀번호 불일치
    if password != password_check:
        raise HTTPException(400, "비밀번호 확인과 다릅니다")


async def password_update_controller(email: str, password: str, password_check: str):

    # 입력값 검증
    validate_password(password, password_check)

    # 저장(Model 계층 호출)
    return update_password(email, password)
