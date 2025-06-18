# app/services/cycle_service.py

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User, UserCycle
from app.schemas import CycleCreate, PaginationMeta, CycleUpdate
from fastapi import HTTPException, status
from app.core.utils import filter_user_cycle_by_auth


def get_cycles_service(
    db: Session,
    user: Optional[User],
    session_id: str,
    search: Optional[str],
    page: int,
    per_page: int,
) -> tuple[List[UserCycle], int]:
    query = filter_user_cycle_by_auth(db.query(UserCycle), user, session_id)
    
    if user:
        query = query.filter(UserCycle.user_id == user.id)
    else:
        query = query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )

    if search:
        query = query.filter(
            or_(
                UserCycle.title.ilike(f"%{search}%"),
                UserCycle.description.ilike(f"%{search}%")
            )
        )

    total = query.count()
    offset = (page - 1) * per_page

    cycles = query.order_by(UserCycle.created_at.desc()).offset(offset).limit(per_page).all()

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
    
    return meta, cycles


def create_cycle_service(
    db: Session,
    user: Optional[User],
    session_id: str,
    data: CycleCreate
) -> UserCycle:
    new_cycle = UserCycle(
        user_id=user.id if user else None,
        session_id=None if user else session_id,
        title=data.title,
        description=data.description,
        total_rounds=data.total_rounds,
        cycle_rest_seconds=data.cycle_rest_seconds
    )
    db.add(new_cycle)     # INSERT 쿼리가 "준비됨"
    db.commit()           # 실제 DB에 INSERT 실행됨
    db.refresh(new_cycle) # 새로 INSERT된 new_cycle의 ID 등 정보를 다시 로딩함
    return new_cycle

def get_cycle_by_id_service(
    id: int,
    user: Optional[User],
    session_id: str,
    db: Session
) -> UserCycle:
    data_by_id = db.query(UserCycle).filter(UserCycle.id == id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )
    return cycle

def update_cycle_service(
        id: int,
        data: CycleUpdate,
        user: Optional[User],
        session_id: str,
        db: Session
) -> UserCycle:
    data_by_id = db.query(UserCycle).filter(UserCycle.id == id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
        # 업데이트
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cycle, field, value)
    
    db.commit()
    db.refresh(cycle)

    return cycle

def delete_cycle_service(
        id: int,
        user: Optional[User],
        session_id: str,
        db: Session
): 
    data_by_id = db.query(UserCycle).filter(UserCycle.id == id)
    query = filter_user_cycle_by_auth(data_by_id, user, session_id)
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    
    # 소프트 삭제
    from datetime import datetime
    cycle.deleted_at = datetime.utcnow()
    db.commit()
    return "Cycle deleted successfully"

# cycle_by_id(), update_cycle(), delete_cycle() 등도 같은 방식으로 추가 가능
