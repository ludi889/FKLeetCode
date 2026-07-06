from fastapi import FastAPI
from app.api.problems import router as problems_router
from app.api.variants import router as variant_router
from app.services.variant_service import VariantService
from contextlib import asynccontextmanager
import app.models

app = FastAPI(title="FKLeetCode")
app.include_router(problems_router)
app.include_router(variant_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.variant_service = VariantService()
    
    yield    
    pass

@app.get("/health")
async def health():
    return {"status": "ok"}