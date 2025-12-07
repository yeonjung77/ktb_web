from fastapi import APIRouter, Form
from BE.controllers.password_controller import password_update_controller

router = APIRouter(
    prefix="/password",
    tags=["password"]
)

@router.put("/update")
async def update_password(
    email: str = Form(...),
    password: str = Form(...),
    password_check: str = Form(...)
):
    return await password_update_controller(email, password, password_check)
