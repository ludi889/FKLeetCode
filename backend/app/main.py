from fastapi import FastAPI
from app.api.problems import router as problems_router
import app.models

app = FastAPI(title="FKLeetCode")
app.include_router(problems_router)


@app.get("/health")
async def health():
    return {"status": "ok"}