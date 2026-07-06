from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemRead

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("/")
async def create_problem(payload: ProblemCreate, db: AsyncSession = Depends(get_db)) -> ProblemRead:
    problem = Problem(**payload.model_dump())
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem