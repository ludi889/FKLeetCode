from app.services.judge_service import JudgeModel
from app.schemas.judge import JudgeRequest, JudgeResult, TestCaseResult
from app.db.session import AsyncSessionLocal
from app.models.submissions import Submission
from sqlalchemy import select
from datetime import datetime, timezone


async def ping(ctx) -> str:
    return "pong"

async def judge_submission(ctx, payload: dict) -> dict:
    job_id = ctx["job_id"]
    request = JudgeRequest(**payload)
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Submission).where(Submission.job_id == job_id))
        submission = result.scalar_one_or_none()
        if submission is None:
            return JudgeResult(status="error", results=[], error="submission row not found").model_dump()
        submission.status = "running"
        await db.commit()
    try:
        results = []
        for case in request.test_cases:
            outcome = JudgeModel.run_code(request.code, case.input)
            if "error" in outcome:
                results.append(TestCaseResult(test_case_id=case.id, passed=False, error=outcome["error"]))
            else:
                results.append(TestCaseResult(
                    test_case_id=case.id,
                    passed=outcome["output"] == case.expected,
                    actual_output=outcome["output"],
                ))
            judge_result = JudgeResult(status="completed", results=results).model_dump()
            final_status = "completed"
    except Exception as e:
        judge_result = JudgeResult(status="error", results=[], error=str(e)).model_dump()
        final_status = "failed"
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Submission).where(Submission.job_id == job_id))
        submission = result.scalar_one_or_none()
        if submission:
            submission.status = final_status
            submission.result = judge_result
            submission.completed_at = datetime.now(timezone.utc)
    return judge_result