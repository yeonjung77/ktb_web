from fastapi import HTTPException, UploadFile
from models.post_edit_model import update_post

def validate_title(title: str):
    if not title:
        raise HTTPException(400, "제목을 입력해주세요")

    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지 작성 가능합니다.")


async def validate_image(image: UploadFile | None):
    if image is None:
        return None

    # 확장자 검사
    if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "이미지 파일만 업로드할 수 있습니다.")

    return image.filename


async def post_edit_controller(post_id: int, title: str, content: str, image: UploadFile | None):
    
    validate_title(title)

    if not content:
        raise HTTPException(400, "내용을 입력해주세요")

    image_filename = await validate_image(image)

    result = update_post(post_id, title, content, image_filename)
    if result is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")

    return result
