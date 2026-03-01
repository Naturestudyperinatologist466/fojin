from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.elasticsearch import close_es, init_es
from app.api import search, texts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await init_es()
    yield
    # Shutdown
    await app.state.redis.close()
    await close_es()


app = FastAPI(
    title="佛津 FoJin API",
    description="全球佛教古籍数字资源聚合平台",
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api")
app.include_router(texts.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
