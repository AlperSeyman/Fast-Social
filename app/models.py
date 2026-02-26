import uuid
from datetime import datetime, UTC
from sqlalchemy import String, Text, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    caption: Mapped[str| None ] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    imagekit_id: Mapped[str | None] = mapped_column(String, nullable=True)