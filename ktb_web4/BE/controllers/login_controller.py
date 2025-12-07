import re
from fastapi import HTTPException, status
from pydantic import BaseModel

from BE.models.login_model import check_credentials


# 요청 body 스키마 (편하게 쓰기 위한 Pydantic 모델)
class LoginRequest(BaseModel):
    email: str
    password: str


def validate_email(email: str):
    email = email.strip()

    # 입력 안 한 경우
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일을 입력해주세요"
        )

    # 너무 짧은 경우 (예: a@b.c 이런 것도 걸고 싶으면 길이 체크)
    if len(email) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 주소 형식을 입력해주세요. (예 : example@example.com)"
        )

    # 간단한 형식 체크 (정규식)
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 주소 형식을 입력해주세요. (예 : example@example.com)"
        )


def validate_password(password: str):
    # 비밀번호 입력 안했을 때
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호를 입력해주세요"
        )

    # 길이 체크
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
        )

    # 각 조건 체크: 대문자, 소문자, 숫자, 특수문자
    if not re.search(r"[A-Z]", password) \
       or not re.search(r"[a-z]", password) \
       or not re.search(r"[0-9]", password) \
       or not re.search(r"[^\w]", password):  # 특수문자
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다."
        )


def login_controller(request: LoginRequest) -> dict:
    """
    Route에서 호출하는 컨트롤러.
    1. 이메일/비밀번호 유효성 검사
    2. Model 계층에 로그인 확인 요청
    3. 결과에 맞춰 JSON 반환 또는 예외 발생
    """
    # 1) 입력값 검증
    validate_email(request.email)
    validate_password(request.password)

    # 2) 실제 로그인 체크 (Model 호출)
    result = check_credentials(request.email, request.password)

    # 3) 로그인 실패 (아이디/비밀번호 틀림)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )

    # 4) 로그인 성공
    # 프론트에서는 이 응답을 보고 게시글 목록 페이지로 이동시키면 됨
    return result
