from pydantic import BaseModel
from typing import Optional
class PostGenerateAndSaveVariantResponseModel(BaseModel):
    id: Optional[str] = None
    translated_statement: Optional[str] = None
    is_valid: bool