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
from app.schemas import PostCreate, PostResponse

router = APIRouter()

# get all posts
@router.get("", response_model=list[PostResponse])
async def get_all_posts(db: Annotated[AsyncSession, Depends(get_db)], limit: int | None=None):

    result = await db.execute(select(models.Post).order_by(models.Post.created_at.desc()))
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


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    await db.delete(post)
    await db.commit()