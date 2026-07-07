from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    status: str
    result: dict
    submitted_at: datetime
    completed_at: datetime
