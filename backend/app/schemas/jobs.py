from pydantic import BaseModel, Field


class PostEnqueueJobResponseModel(BaseModel):
    job_id: str

class GetJobStatusResponseModel(BaseModel):
    status: str
    result: str | None = None

class SubmitCodePayloadModel(BaseModel):
    code: str = Field(max_length=20_000)