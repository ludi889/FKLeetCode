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
async def create_session(
    request: Request, # <-- Injected to access variant_service
    request_data: PostCreateSessionRequestModel | None = None, 
    db: AsyncSession = Depends(get_db)
) -> SessionModel:
    
    if request_data and request_data.variant_id:
        variant = await db.get(ProblemVariant, request_data.variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Requested variant not found")
        problem = await db.get(Problem, variant.problem_id)
    else:
        if request_data and request_data.problem_id:
            query = select(Problem).where(Problem.id == request_data.problem_id)
        elif request_data and request_data.target_difficulty:
            query = select(Problem).where(Problem.difficulty == request_data.target_difficulty)
        else:
            query = select(Problem)
            
        possible_problems = await db.execute(
            query.options(selectinload(Problem.variants)).order_by(func.random()).limit(1)
        )
        problem = possible_problems.scalar_one_or_none()
        
        if not problem:
            raise HTTPException(status_code=404, detail="No valid problem found for provided constraints")
            
        valid_variants = [v for v in problem.variants if v.validated]
        
        if valid_variants:
            variant = random.choice(valid_variants)
        else:
            variant_service = request.app.state.variant_service
            
            try:
                payload = await variant_service.create_variant_payload(
                    statement=problem.statement,
                    signature=problem.signature
                )
                
                new_variant = ProblemVariant(
                    problem_id=problem.id,
                    scenario_context=payload["scenario_context"],
                    stage_1_mvp=payload["stage_1_mvp"],
                    stage_2_curveball=payload["stage_2_curveball"],
                    stage_3_system=payload["stage_3_system"],
                    technical_rubric=payload["technical_rubric"],
                    system_rubric=payload["system_rubric"],
                    communication_rubric=payload["communication_rubric"],
                    embedding=payload["embedding"],
                    validated=True
                )
                db.add(new_variant)
                await db.commit()
                await db.refresh(new_variant)
                variant = new_variant
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"On-the-fly variant generation failed: {str(e)}")

    session = Session(
        problem_id=problem.id,
        problem_variant_id=variant.id,
        status="pending"
    )
    
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