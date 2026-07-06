# backend/tests/test_quality_eval.py
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.metrics import GEval
from app.services.variant_service import VariantService
from app.core.config import settings
from .eval_llm import JudgeModel

@pytest.fixture
def real_variant_service():
    return VariantService()

@pytest.mark.asyncio
async def test_variant_quality(real_variant_service, ensure_ollama_running):
    original_statement = "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."
    signature = {"input": ["List[int]", "int"], "output": "List[int]"}
    
    payload = await real_variant_service.create_variant_payload(
        statement=original_statement,
        signature=signature
    )
    generated_story = payload["translated_statement"]

    eval_model = JudgeModel()
    
    quality_metric = GEval(
        name="Variant Constraint Adherence",
        criteria="Determine if the 'actual output' logically requires processing a list of numbers and an integer to return a list of integers.",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        model=eval_model,
        threshold=0.7
    )

    test_case = LLMTestCase(
        input=original_statement,
        actual_output=generated_story,
    )

    assert_test(test_case, [quality_metric])