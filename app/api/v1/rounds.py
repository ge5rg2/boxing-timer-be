from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.cycle import (
    RoundCreate, RoundUpdate, RoundResponse
)
from app.schemas.response import ApiResponse
from app.dependencies import get_current_user, get_session_id
from app.services.round_service import get_rounds_service, create_round_service, update_round_service, delete_round_service

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[RoundResponse]])
async def get_rounds(
    cycle_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """해당 사이클의 라운드 목록 조회"""
    rounds = get_rounds_service(db, cycle_id, current_user, session_id)
    
    return ApiResponse(
        message="Rounds retrieved successfully",
        data=[RoundResponse.model_validate(round) for round in rounds]
    )


@router.post("/", response_model=ApiResponse[RoundResponse])
async def create_round(
    cycle_id: int,
    round_data: RoundCreate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """라운드 추가"""
    # 사이클 권한 확인
    new_round = create_round_service(
        cycle_id=cycle_id,
        data=round_data,
        user=current_user,
        session_id=session_id,
        db=db
    )
    
    return ApiResponse(
        message="Round created successfully",
        data=RoundResponse.from_orm(new_round)
    )


@router.patch("/{round_id}", response_model=ApiResponse[RoundResponse])
async def update_round(
    cycle_id: int,
    round_id: int,
    round_data: RoundUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """라운드 수정"""
    # 사이클 권한 확인
    round_obj = update_round_service(
        cycle_id=cycle_id,
        round_id=round_id,
        data=round_data,
        user=current_user,
        session_id=session_id,
        db=db
    )
    
    return ApiResponse(
        message="Round updated successfully",
        data=RoundResponse.model_validate(round_obj)
    )


@router.delete("/{round_id}", response_model=ApiResponse[str])
async def delete_round(
    cycle_id: int,
    round_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    delete_round_service(cycle_id, round_id, current_user, session_id, db)
    
    return ApiResponse(
        message="Round deleted successfully",
        data="Round has been deleted"
    )