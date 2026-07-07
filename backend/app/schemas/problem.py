import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class ProblemCreate(BaseModel):
    title: str
    statement: str
    signature: dict      
    constraints: dict
    reference_solution: str
    test_cases: dict     
    difficulty: str
    tags: dict

class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    statement: str       
    signature: dict      
    constraints: dict
    test_cases: dict
    difficulty: str
    tags: dict
    created_at: datetime

class GetProblemsResponseModel(BaseModel):
    problems: List[ProblemRead]