import json
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import get_chat_model
from app.services.embeddings import get_embeddings

class VariantService:
    def __init__(self):
        self.llm = get_chat_model()
        self.embeddings = get_embeddings()
        
        # 2. Define the strict behavior rules for the LLM
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
        
        # 3. Chain the prompt and the LLM together
        self.chain = self.prompt | self.llm

    async def generate_text(self, statement: str, signature: dict) -> str:
        signature_str = json.dumps(signature, indent=2)
        response = await self.chain.ainvoke({
            "statement": statement,
            "signature": signature_str
        })
        return response.content.strip()

    async def generate_vector(self, text: str) -> list[float]:
        return await self.embeddings.aembed_query(text)

    async def create_variant_payload(self, statement: str, signature: dict) -> dict:
        translated_text = await self.generate_text(statement, signature)
        
        vector = await self.generate_vector(translated_text)
        
        return {
            "translated_statement": translated_text,
            "embedding": vector
        }