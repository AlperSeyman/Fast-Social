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

imagekit = ImageKit(private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),)