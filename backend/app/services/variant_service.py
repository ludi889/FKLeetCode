import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.prompts import ChatPromptTemplate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from app.services.llm import get_chat_model
from app.services.embeddings import get_embeddings
from app.services.judge_service import JudgeModel
from app.models.problem import ProblemVariant
from app.schemas.problem import GeneratedVariantSchema

class VariantService:
    def __init__(self):
        self.llm = get_chat_model()
        self.embeddings = get_embeddings()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert technical interviewer and system architect. "
             "Your goal is to disguise a standard algorithmic problem into a progressive, "
             "real-world 3-stage interview scenario. "
             "\n\nRules:"
             "\n- DO NOT output code."
             "\n- Stage 1 must logically enforce the EXACT required signature."
             "\n- Create strict, objective grading rubrics for the human and AI to use."
            ),
            ("human", 
             "ORIGINAL STATEMENT:\n{statement}\n\n"
             "REQUIRED SIGNATURE:\n{signature}\n\n"
             "Generate the progressive scenario and rubrics."
            )
        ])
        
        self.chain = self.prompt | self.llm.with_structured_output(GeneratedVariantSchema)

    async def generate_structured_variant(self, statement: str, signature: dict) -> GeneratedVariantSchema:
        """Returns a strongly-typed Pydantic object instead of a string."""
        response = await self.chain.ainvoke({
            "statement": statement,
            "signature": json.dumps(signature, indent=2)
        })
        return response

    async def generate_vector(self, text: str) -> list[float]:
        return await self.embeddings.aembed_query(text)

    async def validate_variant(self, original_statement: str, generated_variant: GeneratedVariantSchema) -> bool:
        """
        Validation must now compare the original statement to the COMBINED context and MVP.
        Stage 2 and 3 don't dictate the exact input/output, so they shouldn't be penalized by GEval.
        """
        judge = JudgeModel()
        metric = GEval(
            name="Constraint Preservation",
            criteria="Does the generated Stage 1 MVP logically require the exact same inputs, outputs, and algorithmic complexity as the original problem?",
            evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
            model=judge,
            threshold=0.7,
        )
        
        actual_output = f"Context: {generated_variant.scenario_context}\nTask: {generated_variant.stage_1_mvp}"
        
        test_case = LLMTestCase(input=original_statement, actual_output=actual_output)
        metric.measure(test_case)
        return metric.score >= metric.threshold

    async def find_similar_variant(
        self,
        db: AsyncSession,
        problem_id: uuid.UUID,
        embedding: list[float],
        threshold: float = 0.15,
    ) -> ProblemVariant | None:
        result = await db.execute(
            select(ProblemVariant)
            .where(ProblemVariant.problem_id == problem_id)
            .order_by(ProblemVariant.embedding.cosine_distance(embedding))
            .limit(1)
        )
        closest = result.scalar_one_or_none()
        
        if closest:
            return closest
        return None             

    async def create_variant_payload(self, statement: str, signature: dict) -> dict:
        variant_data: GeneratedVariantSchema = await self.generate_structured_variant(statement, signature)
        
        vector = await self.generate_vector(variant_data.scenario_context)
        
        payload = variant_data.model_dump()
        payload["embedding"] = vector
        
        return payload