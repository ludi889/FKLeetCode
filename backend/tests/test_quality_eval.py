import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.metrics import GEval
from app.services.variant_service import VariantService
from app.services.judge_service import JudgeModel

@pytest.fixture
def real_variant_service():
    return VariantService()

@pytest.mark.asyncio
async def test_variant_quality(real_variant_service):
    original_statement = "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."
    signature = {"input": ["List[int]", "int"], "output": "List[int]"}
    
    payload = await real_variant_service.create_variant_payload(
        statement=original_statement,
        signature=signature
    )
    
    assert "scenario_context" in payload
    assert "stage_1_mvp" in payload
    assert "stage_2_curveball" in payload
    assert "stage_3_system" in payload
    assert "technical_rubric" in payload
    assert "embedding" in payload
    assert len(payload["embedding"]) == 768  # Assuming standard pgvector size

    combined_story = f"Context: {payload['scenario_context']}\nTask: {payload['stage_1_mvp']}"

    eval_model = JudgeModel()
    
    quality_metric = GEval(
        name="Variant Constraint Adherence",
        evaluation_steps=[
            "Read the 'Context' to understand the real-world scenario.",
            "Read the 'Task' to identify the required logical input/output shape.",
            "Compare that implied shape against the original input: a list of numbers and a target integer, returning a list of two integer indices.",
            "Do not penalize the output for lacking literal code, variables, or computations. It should be a narrative problem statement.",
            "Score high only if the underlying mathematical/logical constraints match perfectly.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        model=eval_model,
        threshold=0.7,
        verbose_mode=True
    )

    test_case = LLMTestCase(
        input=original_statement,
        actual_output=combined_story,
    )

    assert_test(test_case, [quality_metric])