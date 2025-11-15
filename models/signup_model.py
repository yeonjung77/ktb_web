USERS = []  # [{"email": "..", "password": "..", "nickname": "..", "profile": ".."}]

def is_email_duplicate(email: str) -> bool:
    return any(user["email"] == email for user in USERS)


def is_nickname_duplicate(nickname: str) -> bool:
    return any(user["nickname"] == nickname for user in USERS)


def save_user(email: str, password: str, nickname: str, profile_image: str | None):
    new_user = {
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile": profile_image
    }
    USERS.append(new_user)

    return {"success": True, "message": "회원가입이 완료되었습니다.", "next_url": "/login"}