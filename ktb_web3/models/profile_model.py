from models.signup_model import USERS

def get_user(email: str):
    for user in USERS:
        if user["email"] == email:
            return user
    return None


def update_user(email: str, new_nickname: str, new_profile: str | None):
    user = get_user(email)
    if not user:
        return {"success": False, "message": "유저를 찾을 수 없습니다."}

    user["nickname"] = new_nickname
    if new_profile:
        user["profile"] = new_profile

    return {"success": True, "message": "수정완료"}


def delete_user(email: str):
    global USERS
    USERS = [user for user in USERS if user["email"] != email]

    return {
        "success": True,
        "message": "회원탈퇴가 완료되었습니다.",
        "next_url": "/login"
    }