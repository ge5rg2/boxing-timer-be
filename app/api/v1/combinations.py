from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.combination import (
    CombinationCreate, CombinationUpdate, CombinationResponse
)
from app.schemas.cycle import (
    RoundCombinationResponse
)
from app.schemas.response import ApiResponse, PaginatedResponse
from app.dependencies import get_current_user, get_session_id
from app.services.combination_service import get_combinations_service, create_combination_service, update_combination_service, delete_combination_service, get_combination_by_round_id_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CombinationResponse])
async def get_combinations(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """내 컴비네이션 전체 보기"""
    combinations, meta = get_combinations_service(page, per_page, search, current_user, session_id, db)
    
    return PaginatedResponse(
        message="Combinations retrieved successfully",
        data=[CombinationResponse.model_validate(combo) for combo in combinations],
        meta=meta
    )


@router.post("/", response_model=ApiResponse[CombinationResponse])
async def create_combination(
    combination_data: CombinationCreate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """새 컴비네이션 등록"""
    new_combination = create_combination_service(combination_data, current_user, session_id, db)
    
    return ApiResponse(
        message="Combination created successfully",
        data=CombinationResponse.model_validate(new_combination)
    )


@router.patch("/{combination_id}", response_model=ApiResponse[CombinationResponse])
async def update_combination(
    combination_id: int,
    combination_data: CombinationUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """컴비네이션 수정"""
    combination = update_combination_service(combination_id, combination_data, current_user, session_id,db)
    
    return ApiResponse(
        message="Combination updated successfully",
        data=CombinationResponse.model_validate(combination)
    )


@router.delete("/{combination_id}", response_model=ApiResponse[str])
async def delete_combination(
    combination_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """컴비네이션 삭제 (소프트 삭제)"""
    delete_combination_service(combination_id, current_user, session_id, db)
    
    return ApiResponse(
        message="Combination deleted successfully",
        data="Combination has been deleted"
    )


# 라운드 컴비네이션 관리 엔드포인트
@router.get("/rounds/{round_id}/combinations", response_model=ApiResponse[List[RoundCombinationResponse]])
async def get_round_combinations(
    round_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    new_round_combination = get_combination_by_round_id_service(round_id, current_user, session_id, db)
    
    return ApiResponse(
        message="Round combination added successfully",
        data=RoundCombinationResponse.from_orm(new_round_combination)
    )