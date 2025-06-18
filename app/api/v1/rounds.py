from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserCycle, UserRound
from app.schemas.cycle import (
    RoundCreate, RoundUpdate, RoundResponse
)
from app.schemas.response import ApiResponse
from app.dependencies import get_current_user, get_session_id

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[RoundResponse]])
async def get_rounds(
    cycle_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """해당 사이클의 라운드 목록 조회"""
    # 사이클 권한 확인
    cycle_query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        cycle_query = cycle_query.filter(UserCycle.user_id == current_user.id)
    else:
        cycle_query = cycle_query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    cycle = cycle_query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )
    
    # 라운드 목록 조회
    rounds = db.query(UserRound).filter(
        UserRound.user_cycle_id == cycle_id
    ).order_by(UserRound.round_number).all()
    
    return ApiResponse(
        message="Rounds retrieved successfully",
        data=[RoundResponse.model_validate(round) for round in rounds]
    )


@router.post("/", response_model=ApiResponse[RoundResponse])
async def create_round(
    cycle_id: int,
    round_data: RoundCreate,
    current_user: Optional[User] = Depends(get_current_user),
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """라운드 추가"""
    # 사이클 권한 확인
    cycle_query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        cycle_query = cycle_query.filter(UserCycle.user_id == current_user.id)
    else:
        cycle_query = cycle_query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    cycle = cycle_query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    
    # 중복 라운드 번호 확인
    existing_round = db.query(UserRound).filter(
        UserRound.user_cycle_id == cycle_id,
        UserRound.round_number == round_data.round_number
    ).first()
    
    if existing_round:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Round number already exists"
        )
    
    # 사이클 최대 라운드 수 확인
    if round_data.round_number > cycle.total_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Round number exceeds total rounds ({cycle.total_rounds})"
        )
    
    # 새 라운드 생성
    new_round = UserRound(
        user_cycle_id=cycle_id,
        round_number=round_data.round_number,
        duration_seconds=round_data.duration_seconds,
        rest_seconds=round_data.rest_seconds
    )
    
    db.add(new_round)
    db.commit()
    db.refresh(new_round)
    
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
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    """라운드 수정"""
    # 사이클 권한 확인
    cycle_query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        cycle_query = cycle_query.filter(UserCycle.user_id == current_user.id)
    else:
        cycle_query = cycle_query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    cycle = cycle_query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    
    # 라운드 조회
    round_obj = db.query(UserRound).filter(
        UserRound.id == round_id,
        UserRound.user_cycle_id == cycle_id
    ).first()
    
    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found"
        )
    
    # 업데이트
    update_data = round_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(round_obj, field, value)
    
    db.commit()
    db.refresh(round_obj)
    
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
    """라운드 삭제"""
    # 사이클 권한 확인
    cycle_query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        cycle_query = cycle_query.filter(UserCycle.user_id == current_user.id)
    else:
        cycle_query = cycle_query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    cycle = cycle_query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    
    # 라운드 조회 및 삭제
    round_obj = db.query(UserRound).filter(
        UserRound.id == round_id,
        UserRound.user_cycle_id == cycle_id
    ).first()
    
    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found"
        )
    
    db.delete(round_obj)
    db.commit()
    
    return ApiResponse(
        message="Round deleted successfully",
        data="Round has been deleted"
    )