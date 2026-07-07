from fastapi import FastAPI
from app.api.problems import router as problems_router
from app.api.variants import router as variant_router
from app.api.jobs import router as jobs_router
from app.api.submissions import router as submissions_router
from app.core.config import settings
from app.services.variant_service import VariantService
from contextlib import asynccontextmanager
import app.models

from arq import create_pool
from arq.connections import RedisSettings
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    app.state.variant_service = VariantService()

    yield    
    await app.state.arq_pool.close()
app = FastAPI(title="FKLeetCode", lifespan=lifespan)
app.include_router(problems_router)
app.include_router(variant_router)
app.include_router(jobs_router)
app.include_router(submissions_router)



@app.get("/health")
async def health():
    return {"status": "ok"}