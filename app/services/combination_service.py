from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User, UserCombination, UserRound, UserRoundCombination
from app.core.utils import filter_user_combination_by_auth, filter_user_cycle_by_auth
from app.schemas.response import PaginationMeta
from app.schemas.combination import CombinationCreate, CombinationResponse
from app.schemas.cycle import RoundCombinationCreate

def get_combinations_service(
          page: int,
          per_page: int,
          search: Optional[str],
          user: Optional[User],
          session_id: Optional[str],
          db: Session
) -> tuple[List[UserCombination], int]:
    query = filter_user_combination_by_auth(db.query(UserCombination), user, session_id)
    
        # 검색 조건
    if search:
        query = query.filter(
            or_(
                UserCombination.title.ilike(f"%{search}%"),
                UserCombination.description.ilike(f"%{search}%")
            )
        )
    
    # 전체 개수
    total = query.count()
    
    # 페이지네이션
    offset = (page - 1) * per_page
    combinations = query.order_by(UserCombination.created_at.desc()).offset(offset).limit(per_page).all()
    
    # 메타데이터 계산
    pages = (total + per_page - 1) // per_page
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )

    return combinations, meta

def create_combination_service(
        data: CombinationCreate,
        user: Optional[User],
        session_id: Optional[str],
        db: Session
) -> UserCombination:
    new_combination = UserCombination(
        user_id=user.id if user else None,
        title=data.title,
        description=data.description,
        audio_url=data.audio_url,
        audio_duration_seconds=data.audio_duration_seconds,
        audio_file_size=data.audio_file_size
    )
    db.add(new_combination)
    db.commit()
    db.refresh(new_combination)
    return new_combination

def update_combination_service(
        combination_id: int,
        data: CombinationCreate,
        user: Optional[User],
        session_id: Optional[str],
        db: Session
) -> CombinationResponse:
    data_by_id = db.query(UserCombination).filter(UserCombination.id == combination_id)
    query = filter_user_combination_by_auth(data_by_id, user, session_id)
    combination = query.first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found or no permission"
        )
        # 업데이트
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(combination, field, value)
    
    db.commit()
    db.refresh(combination)

    return combination

def delete_combination_service(
        combination_id: int,
        user: Optional[User],
        session_id: Optional[str],
        db: Session
):
    data_by_id = db.query(UserCombination).filter(UserCombination.id == combination_id)
    query = filter_user_combination_by_auth(data_by_id, user, session_id)
    combination = query.first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found or no permission"
        )
        # 소프트 삭제
    from datetime import datetime
    combination.deleted_at = datetime.utcnow()
    db.commit()

    return None

def get_combination_by_round_id_service(
        round_id: int,
        user: Optional[User],
        session_id: Optional[str],
        db: Session
):
    data_by_id = db.query(UserRound).filter(UserRound.id == round_id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    round_obj = query.first()
    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found"
        )
    # 라운드 컴비네이션 조회
    round_combinations = db.query(UserRoundCombination).filter(
        UserRoundCombination.user_round_id == round_id
    ).order_by(UserRoundCombination.start_time, UserRoundCombination.execution_order).all()

    return round_combinations

def add_round_combination_service(
        round_id: int,
        data: RoundCombinationCreate,
        user: Optional[User],
        session_id: Optional[str],
        db: Session
): 
    data_by_id = db.query(UserRound).filter(UserRound.id == round_id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    round_obj = query.first()

    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found or no permission"
        )
     # 컴비네이션 존재 확인
    combination = db.query(UserCombination).filter(
        UserCombination.id == data.user_combination_id,
        UserCombination.deleted_at.is_(None)
    ).first()

    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found"
        )
    
    # 새 라운드 컴비네이션 생성
    new_round_combination = UserRoundCombination(
        user_round_id=round_id,
        user_combination_id=data.user_combination_id,
        start_time=data.start_time,
        duration=data.duration,
        execution_order=data.execution_order
    )
    
    db.add(new_round_combination)
    db.commit()
    db.refresh(new_round_combination)
        
    return new_round_combination