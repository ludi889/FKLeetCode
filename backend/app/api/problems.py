from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemRead, GetProblemsResponseModel

router = APIRouter(prefix="/problems", tags=["Problems"])


@router.post("/")
async def create_problem(payload: ProblemCreate, db: AsyncSession = Depends(get_db)) -> ProblemRead:
    problem = Problem(**payload.model_dump())
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem

@router.get("/")
async def get_problems(db: AsyncSession = Depends(get_db)) -> GetProblemsResponseModel:
    result = await db.execute(select(Problem))
    problems = result.scalars().all()
    return GetProblemsResponseModel(problems=problems)

@router.get("/{problem_id}")
async def get_problem(problem_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProblemRead:
    problem = await db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem