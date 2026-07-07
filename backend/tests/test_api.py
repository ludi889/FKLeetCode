import pytest
from app.schemas.problem import ProblemRead
from app.schemas.variants import PostGenerateAndSaveVariantResponseModel
from app.schemas.jobs import PostEnqueueJobResponseModel, GetJobStatusResponseModel
from app.schemas.sessions import SessionModel
from unittest.mock import patch, AsyncMock
from app.main import app
import asyncio

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
    response = ProblemRead(**response.json())
    assert response.title == "Two Sum"


@pytest.mark.asyncio
async def test_reuses_similar_variant_when_one_exists(client):
    response = await client.post("/problems/", json=TWO_SUM_PAYLOAD)
    response = ProblemRead(**response.json())
    initial_problems_count = await client.get("/problems")
    with patch("app.services.variant_service.VariantService.generate_vector", new_callable=AsyncMock) as mock_embed:
        # First vector is the original
        vector_a = [0.1] * 768
        # Second vector is VERY similar
        vector_b = [0.10001] * 768
        
        mock_embed.side_effect = [vector_a, vector_b]

        # 3. Act: Generate first variant
        resp1 = await client.post(f"/problems/{response.id}/variants")
        resp1 = PostGenerateAndSaveVariantResponseModel(**resp1.json())
        variant1_id = resp1.id

        # 4. Act: Generate second variant (should be similar enough to trigger reuse)
        resp2 = await client.post(f"/problems/{response.id}/variants")
        resp2 = PostGenerateAndSaveVariantResponseModel(**resp2.json())
        variant2_id = resp2.id

        # 5. Assert: They should be the same ID
        assert variant1_id == variant2_id
        # Verify the database didn't create a new row (optional, check count)

@pytest.mark.asyncio
async def test_state_is_populated(client):
    assert hasattr(app.state, "variant_service")
    assert hasattr(app.state, "arq_pool")

@pytest.mark.asyncio
async def test_enqueue_and_poll_ping_job(client):
    job_schedule_response = await client.post("/jobs/ping")
    job_schedule_parsed = PostEnqueueJobResponseModel(**job_schedule_response.json())
    result = None
    for _ in range(20):  # ~10s max, 0.5s between polls
        status_response = await client.get(f"/jobs/{job_schedule_parsed.job_id}")
        status = GetJobStatusResponseModel(**status_response.json())
        if status.status == "complete":
            result = status.result
            break
        await asyncio.sleep(0.5)

    assert result == "pong"

@pytest.mark.asyncio
async def test_session_random_problem(client, db_session):
    session_create_response = await client.post("/sessions/create_session")
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_variant_known(client):
    payload = {"variant_id": None}
    session_create_response = await client.post("/sessions/create_session", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_problem_known(client):
    payload = {"problem_id": None}
    session_create_response = await client.post("/sessions/create_session", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_problem_difficulty_known(client):
    payload = {"difficulty": "easy"}
    session_create_response = await client.post("/sessions/create_session", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_no_variants(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_start(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_stop(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_happy_path(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_wrong_code(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_state_guard(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_concurrent_guard(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_crashing_code(client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_timeout(client):
    pass