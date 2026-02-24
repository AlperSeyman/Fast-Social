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


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    new_post = models.Post(title=post.title, content=post.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return new_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: uuid.UUID):
    pass