from fastapi import HTTPException, UploadFile

from models.post_create_model import create_post

def validate_title(title: str):
    if not title:
        raise HTTPException(400, "제목, 내용을 모두 작성해주세요")

    if len(title) > 26:
        raise HTTPException(400, "제목은 최대 26자까지 작성 가능합니다.")


def validate_content(content: str):
    if not content:
        raise HTTPException(400, "제목, 내용을 모두 작성해주세요")


async def validate_image(image: UploadFile | None):
    if image is None:
        return None

    # 확장자 검사
    if not image.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "이미지 파일만 업로드할 수 있습니다.")

    return image.filename


async def post_create_controller(
    title: str, 
    content: str, 
    image: UploadFile | None,
    email: str
):
    # 1) 제목 검사
    validate_title(title)

    # 2) 본문 검사
    validate_content(content)

    # 3) 이미지 검사
    image_filename = await validate_image(image)

    # 4) 저장
    result = create_post(title, content, image_filename, email)

    return result
