import pytest
# Define your data once so you don't duplicate code
TWO_SUM_PAYLOAD = {
    "title": "Two Sum",
    "statement": "Given an array of integers, return indices...",
    "constraints": {},
    "reference_solution": "def two_sum(): pass",
    "test_cases": {},
    "difficulty": "easy",
    "tags": {"topics": ["arrays"]},
    "signature": {"input": ["List[int]", "int"], "output": "List[int]"}
}

@pytest.mark.asyncio
async def test_create_problem(client):
    response = await client.post("/problems/", json=TWO_SUM_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["title"] == "Two Sum"