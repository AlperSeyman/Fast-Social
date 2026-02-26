from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import posts, images

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(posts.router, prefix="/api/posts", tags=["posts"])