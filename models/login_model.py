VALID_EMAIL = "test@example.com"
VALID_PASSWORD = "Test1234!"

def check_credentials(email: str, password: str) -> dict:
    """
    이메일/비밀번호가 맞는지 확인하고 JSON(dict)만 반환하는 Model 계층 함수
    """
    if email == VALID_EMAIL and password == VALID_PASSWORD:
        return {
            "success": True,
            "message": "로그인에 성공했습니다.",
            "next_url": "/posts"  # 프론트에서 게시글 목록 페이지로 이동할 때 사용
        }
    else:
        return {
            "success": False,
            "message": "아이디 또는 비밀번호를 확인해주세요."
        }