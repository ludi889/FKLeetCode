import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProblemCreate(BaseModel):
    title: str
    statement: str
    constraints: dict
    reference_solution: str
    test_cases: dict
    difficulty: str
    tags: dict


class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    difficulty: str
    tags: dict
    created_at: datetime