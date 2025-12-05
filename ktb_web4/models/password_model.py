from models.signup_model import USERS

def update_password(email: str, new_password: str):
    for user in USERS:
        if user["email"] == email:
            user["password"] = new_password
            return {"success": True, "message": "수정 완료"}

    return {"success": False, "message": "유저를 찾을 수 없습니다."}