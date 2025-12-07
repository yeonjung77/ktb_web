from fastapi import APIRouter, Form, File, UploadFile
from BE.controllers.post_edit_controller import post_edit_controller

router = APIRouter(
    prefix="/posts",
    tags=["post_edit"]
)

@router.put("/{post_id}/edit")
async def edit_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None)
):
    return await post_edit_controller(post_id, title, content, image)
