from fastapi import APIRouter, Request
from arq.jobs import Job, JobStatus
from fastapi import HTTPException,  Depends
from app.schemas.jobs import PostEnqueueJobResponseModel, GetJobStatusResponseModel
from enum import Enum
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

