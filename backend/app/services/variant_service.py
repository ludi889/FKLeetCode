import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from app.services.llm import get_chat_model
from app.services.embeddings import get_embeddings

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

    async def create_variant_payload(self, statement: str, signature: dict) -> dict:
        translated_text = await self.generate_text(statement, signature)
        
        vector = await self.generate_vector(translated_text)
        
        return {
            "translated_statement": translated_text,
            "embedding": vector
        }