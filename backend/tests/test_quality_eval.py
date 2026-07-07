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
    generated_story = payload["translated_statement"]

    eval_model = JudgeModel()
    
    quality_metric = GEval(
        name="Variant Constraint Adherence",
        evaluation_steps=[
            "Identify the input/output shape implied by the actual output: what data would a solver need, and what would they need to return?",
            "Compare that implied shape against: input is a list of numbers and a target integer, output is a list of two integer indices.",
            "The actual output is a narrative problem statement, not a solution or computation — do not penalize it for lacking numbers, code, or a computed answer.",
            "Score high only if the implied input/output shape matches, regardless of how the scenario is dressed up.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        model=eval_model,
        threshold=0.7,
        verbose_mode=True
    )

    test_case = LLMTestCase(
        input=original_statement,
        actual_output=generated_story,
    )

    assert_test(test_case, [quality_metric])