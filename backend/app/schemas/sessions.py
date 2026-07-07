from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid


class SessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    problem_variant_id: str
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None

class GetAllSessionsResponseModel(BaseModel):
    sessions: list[SessionModel] | None = None

class PostCreateSessionRequestModel(BaseModel):
    problem_id: str | None = None
    variant_id: str | None = None
    target_difficulty: str | None = None