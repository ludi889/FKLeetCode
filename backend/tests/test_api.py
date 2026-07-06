import pytest
from app.schemas.problem import ProblemRead
from app.schemas.variants import PostGenerateAndSaveVariantResponseModel
from unittest.mock import patch, AsyncMock
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
    with patch("app.services.variant_service.VariantService.create_vector", new_callable=AsyncMock) as mock_embed:
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