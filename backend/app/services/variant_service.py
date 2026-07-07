import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from app.services.llm import get_chat_model
from app.services.embeddings import get_embeddings
from app.services.judge_service import JudgeModel
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams
from app.models.problem import ProblemVariant
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
import uuid

class VariantService:
    def __init__(self):
        self.llm = get_chat_model()
        self.embeddings = get_embeddings()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert technical interviewer. Rewrite algorithmic problems "
             "into unique, real-world scenarios to prevent candidate memorization. "
             "Be concise. DO NOT output code. DO NOT output constraints. "
             "ONLY output the new story."),
            ("human", 
             "ORIGINAL STATEMENT:\n{statement}\n\n"
             "REQUIRED SIGNATURE:\n{signature}\n\n"
             "Create a new story that logically requires this exact input/output.")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def generate_text(self, statement: str, signature: dict) -> str:
        response_string = await self.chain.ainvoke({
            "statement": statement,
            "signature": json.dumps(signature, indent=2)
        })
        
        return response_string.strip()

    async def generate_vector(self, text: str) -> list[float]:
        return await self.embeddings.aembed_query(text)

    async def validate_variant(self, original_statement: str, translated_statement: str, signature: dict) -> bool:
        judge = JudgeModel()
        metric = GEval(
            name="Constraint Preservation",
            criteria="Does the actual output preserve the same input/output types and logical constraints as the original, without introducing new ambiguity?",
            evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
            model=judge,
            threshold=0.7,
        )
        test_case = LLMTestCase(input=original_statement, actual_output=translated_statement)
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
        if closest and closest.embedding.cosine_distance(embedding) < threshold:
            return closest
        return None

    async def create_variant_payload(self, statement: str, signature: dict) -> dict:
        translated_text = await self.generate_text(statement, signature)
        
        vector = await self.generate_vector(translated_text)
        
        return {
            "translated_statement": translated_text,
            "embedding": vector
        }