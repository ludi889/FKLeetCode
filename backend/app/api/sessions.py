from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.session import Session
from app.schemas.sessions import SessionModel, GetAllSessionsResponseModel, PostCreateSessionRequestModel
from app.models.problem import Problem, ProblemVariant
from app.models.submissions import Submission
import random
from datetime import datetime, timezone
from app.schemas.jobs import PostEnqueueJobResponseModel, SubmitCodePayloadModel
router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/")
async def create_session(request_data: PostCreateSessionRequestModel | None = None,  db: AsyncSession = Depends(get_db)) -> SessionModel:
    count_result = await db.execute(select(func.count(Problem.id)))
    total_problems = count_result.scalar()
    # Find related problem - we will need variants anyway
    if request_data and request_data.variant_id:
        variant = await db.get(ProblemVariant, request_data.variant_id)
    else:
        if request_data and request_data.problem_id:
            possible_problems = await db.execute(select(Problem).where(Problem.id == request_data.problem_id).options(selectinload(Problem.variants)).order_by(func.random()).limit(1))
        elif request_data and request_data.target_difficulty:
            possible_problems = await db.execute(select(Problem).where(Problem.difficulty == request_data.target_difficulty).options(selectinload(Problem.variants)).order_by(func.random()).limit(1))
        else:
            possible_problems = await db.execute(select(Problem).options(selectinload(Problem.variants)).order_by(func.random()).limit(1))
        print(possible_problems)
        problem = possible_problems.scalar_one_or_none()
        if not problem:
            raise HTTPException(status_code=404, detail="No valid problem found for provided constraints")
        valid_variants = [v for v in problem.variants if v.validated]
        if not valid_variants:
            raise HTTPException(status_code=422, detail="No valid variants of the problem found")
        variant = random.choice(valid_variants)
    session = Session(problem_variant_id=variant.id,
                      status="pending")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)) -> SessionModel:
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/")
async def get_all_sessions(request: Request, db: AsyncSession = Depends(get_db)) -> GetAllSessionsResponseModel:
    session_query = await db.execute(select(Session))
    sessions = session_query.scalars().all()
    return GetAllSessionsResponseModel(sessions=sessions)


@router.post("/{session_id}/start")
async def start_session(session_id: str, db: AsyncSession = Depends(get_db)) -> SessionModel:
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="No pending sessions found")

    session.started_at = datetime.now(tz=timezone.utc)
    session.status = "active"
    await db.commit()
    await db.refresh(session)
    return session

@router.post("/{session_id}/stop")
async def stop_session(session_id: str, db: AsyncSession = Depends(get_db)) -> SessionModel:
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="No pending sessions found")

    session.ended_at = datetime.now(tz=timezone.utc)
    session.status = "completed"
    await db.commit()
    await db.refresh(session)
    return session

@router.post("/{session_id}/submit")
async def submit_code(session_id: str, request_data: SubmitCodePayloadModel, request: Request, db: AsyncSession = Depends(get_db)) -> PostEnqueueJobResponseModel:
    session_result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.variant).selectinload(ProblemVariant.problem))
    )
    session: Session | None = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Session is not active.")

    # reject if a submission is already in flight for this session
    existing = await db.execute(
        select(Submission).where(
            Submission.session_id == session_id,
            Submission.status.in_(["queued", "running"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A submission is already running for this session")
    problem_variant: ProblemVariant | None = session.variant
    if not problem_variant:
        raise HTTPException(status_code=404, detail="Problem variant not found")
    if not problem_variant.validated:
        raise HTTPException(status_code=500, detail="Problem variant is unvalidated")
    base_problem: Problem = problem_variant.problem
    test_cases = base_problem.test_cases
    
    job = await request.app.state.arq_pool.enqueue_job(
        "judge_submission",
        {"session_id": session_id, "code": request_data.code, "test_cases": test_cases},
    )
    submission = Submission(
        session_id=session_id,
        code=request_data.code,
        job_id=job.job_id,
        status="queued",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return PostEnqueueJobResponseModel(job_id=job.job_id)