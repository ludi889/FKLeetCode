# backend/tests/test_problems.py
async def test_create_problem(client):
    response = await client.post("/problems/", json={
            "title": "Two Sum",
            "statement": "...",
            "constraints": {},
            "reference_solution": "...",
            "test_cases": {},
            "difficulty": "easy",
            "tags": {"topics": ["arrays"]},
    })
    assert response.status_code == 200
    body = response.json()
    assert "statement" not in body
    assert body["title"] == "Two Sum"