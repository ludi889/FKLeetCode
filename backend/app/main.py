from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.problems import router as problems_router
from app.api.variants import problem_variants_router as problem_variant_router
from app.api.variants import variants_router as variant_router
from app.api.jobs import router as jobs_router
from app.api.submissions import router as submissions_router
from app.api.sessions import router as sessions_router
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
    await app.state.arq_pool.aclose()
app = FastAPI(title="FKLeetCode", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(problems_router)
app.include_router(problem_variant_router)
app.include_router(variant_router)
app.include_router(jobs_router)
app.include_router(submissions_router)
app.include_router(sessions_router)



@app.get("/health")
async def health():
    return {"status": "ok"}