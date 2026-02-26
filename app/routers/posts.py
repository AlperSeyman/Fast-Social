import uuid
from typing import Annotated
from fastapi import (
    APIRouter,
    status,
    Depends,
    Response,
    HTTPException,
    UploadFile,
    File,
    Form
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app import models
from app.database import get_db
from app.schemas import PostResponse, PostUpdate
from app.routers.images import imagekit

router = APIRouter()


# get all posts
@router.get("", response_model=list[PostResponse])
async def get_all_posts(db: Annotated[AsyncSession, Depends(get_db)], limit: int | None=None):

    result = await db.execute(select(models.Post).order_by(models.Post.created_at.desc()).limit(limit))
    posts = result.scalars().all()
    return posts


# get post by id
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@router.post("", response_model=PostResponse)
async def create_post(db: Annotated[AsyncSession, Depends(get_db)], file: UploadFile=File(...), caption: str | None = Form(None)):

    file_bytes = await file.read()

    upload_result = imagekit.files.upload(
        file=file_bytes,
        file_name=file.filename,
        folder="/fast_social_uploads"
    )

    new_post = models.Post(
        caption=caption,
        url=upload_result.url,
        file_type=file.content_type,
        file_name=upload_result.name,
        imagekit_id=upload_result.file_id
    )

    db.add(new_post)

    await db.commit()
    await db.refresh(new_post)

    return new_post

@router.patch("/{post_id}", response_model=PostResponse)
async def update_patch_post(post_id: uuid.UUID, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_post_dict = post_data.model_dump(exclude_unset=True)

    for field, value in update_post_dict.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)

    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.imagekit_id:
        try:
            imagekit.files.delete(post.imagekit_id)
        except Exception as e:
            print(f"Could not delete from ImageKit: {e}")

    await db.delete(post)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)