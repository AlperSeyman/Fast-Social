from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
import uuid

class PostBase(BaseModel):
    title : str = Field(default=None, min_length=1, max_length=100)
    content : str = Field(default=None, min_length=1)

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    model_config=ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime