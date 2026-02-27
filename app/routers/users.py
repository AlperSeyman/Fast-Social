from datetime import timedelta
from typing import Annotated
from fastapi import (
    APIRouter,
    status,
    Depends,
    Response,
    HTTPException,
    UploadFile,
    File,
    Form,

)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import config, database, models
from app.schemas import PostResponse, Token, UserCreate, UserPrivate, UserPublic, UserUpdate
from app.auth import hash_password, create_access_token, verify_password, CurrentUser

from app.routers.images import imagekit

router = APIRouter()


# create a user
@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(database.get_db)]):

    result = await db.execute(select(models.User).where(func.lower(models.User.username) == user.username.lower()))
    existing_username = result.scalars().first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    result = await db.execute(select(models.User).where(func.lower(models.User.email) == user.email.lower()))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(database.get_db)]):

    # Look up user by email (case-insensitive)
    # OAuth2PasswordRequestForm uses "username" field, treat it as email
    result = await db.execute(select(models.User).where(func.lower(models.User.email) == form_data.username.lower()))
    user = result.scalars().first()

    # Verify user exisist and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=config.settings.access_token_expire_minutes)
    access_token = create_access_token(
        data= {"sub" : str(user.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, access_token_expires=access_token_expires)

