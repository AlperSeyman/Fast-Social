from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
import uuid

class PostBase(BaseModel):
    caption: str | None = None
    url : str | None = None
    file_type: str | None = None
    file_name: str | None = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    model_config=ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime