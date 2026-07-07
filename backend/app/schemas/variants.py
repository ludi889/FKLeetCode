from pydantic import BaseModel, ConfigDict
from typing import Optional

class PostGenerateAndSaveVariantResponseModel(BaseModel):
    id: Optional[str] = None
    translated_statement: Optional[str] = None
    is_valid: bool

class GetProblemVariantsResponseEntryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    translated_statement: Optional[str] = None
    is_valid: bool


class GetProblemVariantsResponseModel(BaseModel):
    variants: list[GetProblemVariantsResponseEntryModel]