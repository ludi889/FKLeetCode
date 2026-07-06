from pydantic import BaseModel

class PostGenerateAndSaveVariantResponseModel(BaseModel):
    id: str
    translated_statement: str