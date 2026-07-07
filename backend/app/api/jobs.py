from fastapi import APIRouter, Request
from arq.jobs import Job, JobStatus
from fastapi import HTTPException,  Depends
from app.schemas.jobs import PostEnqueueJobResponseModel, GetJobStatusResponseModel, SubmitCodePayloadModel
from app.models.session import Session
from app.models.problem import ProblemVariant, Problem
from app.models.submissions import Submission
from enum import Enum
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
router = APIRouter(prefix="/jobs", tags=["Jobs"])

class ValidJobs(Enum):
    PING = "ping"

@router.post("/ping")
async def enqueue_ping(request: Request) -> PostEnqueueJobResponseModel:
    job = await request.app.state.arq_pool.enqueue_job(ValidJobs.PING.value)
    return PostEnqueueJobResponseModel(job_id=job.job_id)


@router.get("/{job_id}")
async def get_job_status(job_id: str, request: Request) -> GetJobStatusResponseModel:
    job = Job(job_id, request.app.state.arq_pool)
    status = await job.status()

    if status == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")

    if status != JobStatus.complete:
        return GetJobStatusResponseModel(status="pending")
    info = await job.info()
    return GetJobStatusResponseModel(status="complete", result=info.result)

@router.post("/{session_id}/submit")
async def submit_code(session_id: str, request_data: SubmitCodePayloadModel, request: Request, db: AsyncSession = Depends(get_db)) -> PostEnqueueJobResponseModel:
    # fetch the session -> problem_variant -> problem, pull real test_cases server-side
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