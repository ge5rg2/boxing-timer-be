from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (
    CycleCreate, CycleUpdate, CycleResponse, CycleListResponse
)
from app.schemas import ApiResponse, PaginatedResponse
from app.dependencies import get_current_user, get_session_id
from app.services.cycle_service import get_cycles_service, create_cycle_service, get_cycle_by_id_service, update_cycle_service, delete_cycle_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CycleListResponse])
async def get_cycles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """사이클 목록 조회"""
    meta, cycles = get_cycles_service(db, current_user, session_id, search, page, per_page)
    return PaginatedResponse(
        message="Cycles retrieved successfully",
        data=[CycleListResponse.model_validate(cycle) for cycle in cycles],
        meta=meta
    )


@router.post("/", response_model=ApiResponse[CycleResponse])
async def create_cycle(
    cycle_data: CycleCreate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """새 사이클 생성"""
    new_cycle = create_cycle_service(db, current_user, session_id, cycle_data)
    return ApiResponse(
        message="Cycle created successfully",
        data=CycleResponse.model_validate(new_cycle)
    )


@router.get("/{cycle_id}", response_model=ApiResponse[CycleResponse])
async def get_cycle(
    cycle_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """사이클 상세 조회"""
    cycle = get_cycle_by_id_service(cycle_id, current_user, session_id, db)
    
    return ApiResponse(
        message="Cycle retrieved successfully",
        data=CycleResponse.model_validate(cycle)
    )


@router.patch("/{cycle_id}", response_model=ApiResponse[CycleResponse])
async def update_cycle(
    cycle_id: int,
    cycle_data: CycleUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """사이클 수정"""
    cycle = update_cycle_service(cycle_id, cycle_data, current_user, session_id, db)
    
    return ApiResponse(
        message="Cycle updated successfully",
        data=CycleResponse.model_validate(cycle)
    )


@router.delete("/{cycle_id}", response_model=ApiResponse[str])
async def delete_cycle(
    cycle_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """사이클 삭제 (소프트 삭제)"""
    delete_cycle_service(cycle_id, current_user, session_id, db)
    
    return ApiResponse(
        message="Cycle deleted successfully",
        data="Cycle has been deleted"
    )