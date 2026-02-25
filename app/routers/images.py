import os
from dotenv import load_dotenv
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form


from app.database import get_db
from app import models
from app. schemas import PostCreate, PostResponse
from sqlalchemy.ext.asyncio import AsyncSession

from imagekitio import ImageKit

router = APIRouter()

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)

@router.post("/upload", response_model=PostResponse)
async def upload_file(db: Annotated[AsyncSession, Depends(get_db)], file: UploadFile = File(...), caption: str | None = Form(None)):

    file_bytes = await file.read()

    upload_result = imagekit.files.upload(
        file=file_bytes,
        file_name=file.filename,
        folder="/fast_social_uploads"
    )

    new_post = models.Post(caption=caption, url=upload_result.url, file_type=file.content_type, file_name=upload_result.name)

    db.add(new_post)

    await db.commit()
    await db.refresh(new_post)

    return new_post