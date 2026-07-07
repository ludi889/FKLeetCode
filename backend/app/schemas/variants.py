import uuid
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class PostGenerateAndSaveVariantResponseModel(BaseModel):
    id: Optional[uuid.UUID] = None
    scenario_context: Optional[str] = None
    is_valid: bool

class GetProblemVariantsResponseEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    problem_id: uuid.UUID
    scenario_context: str
    stage_1_mvp: str
    stage_2_curveball: str
    stage_3_system: str
    technical_rubric: dict
    system_rubric: dict
    communication_rubric: dict
    validated: bool

class GetProblemVariantsResponseModel(BaseModel):
    variants: list[GetProblemVariantsResponseEntryModel]

class GeneratedVariantSchema(BaseModel):
    scenario_context: str = Field(..., description="The overarching theme (e.g., 'Logistics coordinator for space cargo'). No coding instructions here.")
    stage_1_mvp: str = Field(..., description="The initial coding task. Must require the exact input/output of the original statement.")
    stage_2_curveball: str = Field(..., description="A sudden requirement change or edge case to test candidate adaptability.")
    stage_3_system: str = Field(..., description="A system design or scaling question based on the scenario.")
    technical_rubric: dict = Field(..., description="Key-value pairs of technical expectations (e.g., 'time_complexity': 'Expected O(N)', 'edge_cases': 'Must handle empty arrays').")
    system_rubric: dict = Field(..., description="Key-value pairs of expected system design concepts.")
    communication_rubric: dict = Field(..., description="Key-value pairs of behavioral/communication checks.")