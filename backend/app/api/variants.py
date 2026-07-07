import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.problem import Problem, ProblemVariant
from app.schemas.variants import (
    PostGenerateAndSaveVariantResponseModel, 
    GetProblemVariantsResponseModel
)
from app.services.variant_service import VariantService
from app.schemas.variants import GeneratedVariantSchema

router = APIRouter(prefix="/problems", tags=["Variants"])

@router.post("/{problem_id}/variants")
async def generate_and_save_variant(
    request: Request,
    problem_id: uuid.UUID, 
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

    schema_for_validation = GeneratedVariantSchema(**payload)

    is_valid = await variant_service.validate_variant(
        original_statement=problem.statement,
        generated_variant=schema_for_validation
    )
    
    if not is_valid:
        return PostGenerateAndSaveVariantResponseModel(is_valid=False)
        
    similar_variant = await variant_service.find_similar_variant(
        db=db, 
        problem_id=problem.id, 
        embedding=payload["embedding"]
    )
    
    if similar_variant:
        new_variant = similar_variant
    else:
        new_variant = ProblemVariant(
            problem_id=problem.id,
            scenario_context=payload["scenario_context"],
            stage_1_mvp=payload["stage_1_mvp"],
            stage_2_curveball=payload["stage_2_curveball"],
            stage_3_system=payload["stage_3_system"],
            technical_rubric=payload["technical_rubric"],
            system_rubric=payload["system_rubric"],
            communication_rubric=payload["communication_rubric"],
            embedding=payload["embedding"],
            validated=True
        )
        db.add(new_variant)
        await db.commit()
        await db.refresh(new_variant)
        
    return PostGenerateAndSaveVariantResponseModel(
        id=new_variant.id, 
        scenario_context=new_variant.scenario_context, 
        is_valid=True
    )

@router.get("/{problem_id}/variants")
async def get_problem_variants(
    problem_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
) -> GetProblemVariantsResponseModel:
    query = select(ProblemVariant).where(ProblemVariant.problem_id == problem_id)
    result = await db.execute(query)
    variants = result.scalars().all()
    
    return GetProblemVariantsResponseModel(variants=variants)