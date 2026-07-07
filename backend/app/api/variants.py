# app/api/variants.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.db.session import get_db
from app.models.problem import Problem, ProblemVariant
from app.schemas.variants import PostGenerateAndSaveVariantResponseModel
from app.services.variant_service import VariantService

router = APIRouter(prefix="/problems", tags=["Variants"])


@router.post("/{problem_id}/variants")
async def generate_and_save_variant(
    request: Request,
    problem_id: str, 
    db: AsyncSession = Depends(get_db)
) -> Optional[PostGenerateAndSaveVariantResponseModel]:
    variant_service: VariantService = request.app.state.variant_service
    problem = await db.get(Problem, problem_id)
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    try:
        payload = await variant_service.create_variant_payload(
            statement=problem.statement,
            signature=problem.signature
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")

    is_valid = await variant_service.validate_variant(original_statement=problem.statement,
                                                      translated_statement=payload["translated_statement"],
                                                      signature=problem.signature)
    if not is_valid:
        return PostGenerateAndSaveVariantResponseModel(is_valid=False)
    new_variant = ProblemVariant(
        problem_id=problem.id,
        translated_statement=payload["translated_statement"],
        embedding=payload["embedding"],
        validated=True
    )
    similar_variant = await variant_service.find_similar_variant(db=db, problem_id=problem.id, embedding=payload["embedding"])
    if similar_variant:
        new_variant = similar_variant
    else:
        db.add(new_variant)
        await db.commit()
        await db.refresh(new_variant)
    response = PostGenerateAndSaveVariantResponseModel(id=new_variant.id, translated_statement=new_variant.translated_statement, is_valid=True)
    return response