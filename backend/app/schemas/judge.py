from pydantic import BaseModel

class TestCase(BaseModel):
    id: str
    input: dict
    expected: object

class JudgeRequest(BaseModel):
    session_id: str
    code: str
    test_cases: list[TestCase]

class TestCaseResult(BaseModel):
    test_case_id: str
    passed: bool
    actual_output: object | None = None
    error: str | None = None

class JudgeResult(BaseModel):
    status: str
    results: list[TestCaseResult]
    error: str | None = None