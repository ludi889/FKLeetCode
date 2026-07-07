import uuid
from pydantic import BaseModel, ConfigDict
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