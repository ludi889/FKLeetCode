from app.models.submissions import Submission
from app.schemas.submissions import SubmissionRead
import uuid
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, APIRouter, Depends
router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get("/{submission_id}")
async def get_submission(submission_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SubmissionRead:
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    return submission