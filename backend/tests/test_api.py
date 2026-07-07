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
    # 1. Setup original problem
    response = await client.post("/problems/", json=TWO_SUM_PAYLOAD)
    problem_id = response.json()["id"]

    # 2. Prepare fake payloads with highly similar embeddings
    vector_a = [0.1] * 768
    vector_b = [0.10001] * 768

    fake_payload_a = {
        "scenario_context": "Logistics in space",
        "stage_1_mvp": "Fake MVP A",
        "stage_2_curveball": "Fake Curveball A",
        "stage_3_system": "Fake System A",
        "technical_rubric": {},
        "system_rubric": {},
        "communication_rubric": {},
        "embedding": vector_a
    }
    
    fake_payload_b = fake_payload_a.copy()
    fake_payload_b["embedding"] = vector_b
    fake_payload_b["scenario_context"] = "A slightly different logistics story"

    with patch("app.api.variants.VariantService.create_variant_payload", new_callable=AsyncMock) as mock_payload, \
         patch("app.api.variants.VariantService.validate_variant", new_callable=AsyncMock) as mock_validate:
        
        mock_payload.side_effect = [fake_payload_a, fake_payload_b]
        
        mock_validate.return_value = True  

        resp1 = await client.post(f"/problems/{problem_id}/variants")
        assert resp1.status_code == 200, resp1.text
        
        data1 = PostGenerateAndSaveVariantResponseModel(**resp1.json())
        assert data1.is_valid is True
        variant1_id = data1.id

        resp2 = await client.post(f"/problems/{problem_id}/variants")
        assert resp2.status_code == 200, resp2.text
        
        data2 = PostGenerateAndSaveVariantResponseModel(**resp2.json())
        assert data2.is_valid is True
        variant2_id = data2.id

        assert variant1_id == variant2_id
        
        assert data2.scenario_context == "Logistics in space"

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
async def test_session_random_problem(seeded_client):
    session_create_response = await seeded_client.post("/sessions/")
    print(session_create_response)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_variant_known(seeded_client):
    payload = {"variant_id": None}
    session_create_response = await seeded_client.post("/sessions/", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_problem_known(seeded_client):
    payload = {"problem_id": None}
    session_create_response = await seeded_client.post("/sessions/", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_problem_difficulty_known(seeded_client):
    payload = {"difficulty": "easy"}
    session_create_response = await seeded_client.post("/sessions/", json=payload)
    session_create_parsed = SessionModel(**session_create_response.json())
    assert session_create_parsed.id

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_no_variants(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_start(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_session_stop(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_happy_path(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_wrong_code(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_state_guard(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_concurrent_guard(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_crashing_code(seeded_client):
    pass

@pytest.mark.asyncio
@pytest.mark.skip
async def test_submission_timeout(seeded_client):
    pass