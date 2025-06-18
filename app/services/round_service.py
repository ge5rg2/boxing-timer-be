from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, UserCycle, UserRound
from app.schemas import RoundCreate, UserRound, RoundUpdate, RoundResponse
from fastapi import HTTPException, status
from app.core.utils import filter_user_cycle_by_auth

def get_rounds_service(
    db: Session,
    cycle_id: int,
    user: Optional[User],
    session_id: str,
) -> UserRound:
    data_by_id = db.query(UserCycle).filter(UserCycle.id == cycle_id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )
    
    # 라운드 목록 조회
    rounds = db.query(UserRound).filter(
        UserRound.user_cycle_id == cycle_id
    ).order_by(UserRound.round_number).all()

    return rounds

def create_round_service(
    cycle_id: int,
    data: RoundCreate,
    user: Optional[User],
    session_id: str,
    db: Session
) -> RoundResponse:
    data_by_id = db.query(UserCycle).filter(UserCycle.id == cycle_id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    # 중복 라운드 번호 확인
    existing_round = db.query(UserRound).filter(
        UserRound.user_cycle_id == cycle_id,
        UserRound.round_number == data.round_number
    ).first()
    if existing_round:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Round number already exists"
        )
    
    # 사이클 최대 라운드 수 확인
    if data.round_number > cycle.total_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Round number exceeds total rounds ({cycle.total_rounds})"
        )

    # 새 라운드 생성
    new_round = UserRound(
        user_cycle_id=cycle_id,
        round_number=data.round_number,
        duration_seconds=data.duration_seconds,
        rest_seconds=data.rest_seconds
    )
    db.add(new_round)
    db.commit()
    db.refresh(new_round)
    
    return new_round

def update_round_service(
    cycle_id: int,
    round_id: int,
    data: RoundUpdate,
    user: Optional[User],
    session_id: str,
    db: Session
): return None

def delete_round_service(
    cycle_id: int,
    round_id: int,
    data: RoundUpdate,
    user: Optional[User],
    session_id: str,
    db: Session
): return None