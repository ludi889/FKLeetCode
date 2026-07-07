import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List


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

class GetProblemsResponseModel(BaseModel):
    problems: List[ProblemRead]


from pydantic import BaseModel, Field

class GeneratedVariantSchema(BaseModel):
    scenario_context: str = Field(..., description="The overarching theme (e.g., 'Logistics coordinator for space cargo'). No coding instructions here.")
    stage_1_mvp: str = Field(..., description="The initial coding task. Must require the exact input/output of the original statement.")
    stage_2_curveball: str = Field(..., description="A sudden requirement change or edge case to test candidate adaptability.")
    stage_3_system: str = Field(..., description="A system design or scaling question based on the scenario.")
    technical_rubric: dict = Field(..., description="Key-value pairs of technical expectations (e.g., 'time_complexity': 'Expected O(N)', 'edge_cases': 'Must handle empty arrays').")
    system_rubric: dict = Field(..., description="Key-value pairs of expected system design concepts.")
    communication_rubric: dict = Field(..., description="Key-value pairs of behavioral/communication checks.")