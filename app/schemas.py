from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
import uuid

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, max_length=120)

class Token(BaseModel):
    access_token: str
    token_type: str


class PostBase(BaseModel):
    caption: str | None = None
    url : str | None = None
    file_type: str | None = None
    file_name: str | None = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    caption: str | None = None


class PostResponse(PostBase):
    model_config=ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    user : UserPublic