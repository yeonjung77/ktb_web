from fastapi import APIRouter, Form, UploadFile, File
from controllers.post_create_controller import post_create_controller

router = APIRouter(
    prefix="/posts",
    tags=["post_create"]
)

@router.post("/create")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    email: str = Form(...),
    image: UploadFile | None = File(None)
):
    return await post_create_controller(title, content, image, email)