# app/api/variants.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.problem import Problem, ProblemVariant
from app.schemas.variants import PostGenerateAndSaveVariantResponseModel
from app.services.variant_service import VariantService

router = APIRouter(prefix="/problems", tags=["Variants"])

variant_service = VariantService()

@router.post("/{problem_id}/variants")
async def generate_and_save_variant(
    problem_id: str, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    try:
        payload = await variant_service.create_variant_payload(
            statement=problem.statement,
            signature=problem.signature
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")

    new_variant = ProblemVariant(
        problem_id=problem.id,
        translated_statement=payload["translated_statement"],
        embedding=payload["embedding"],
        validated=False
    )
    
    db.add(new_variant)
    await db.commit()
    await db.refresh(new_variant)

    return PostGenerateAndSaveVariantResponseModel(id=id, translated_statement=payload["translated_statement"])