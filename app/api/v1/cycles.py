from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, UserCycle
from app.schemas import (
    CycleCreate, CycleUpdate, CycleResponse, CycleListResponse
)
from app.schemas import ApiResponse, PaginatedResponse, PaginationMeta
from app.dependencies import get_current_user, get_session_id

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
    """내 사이클 리스트 조회"""
    query = db.query(UserCycle).filter(UserCycle.deleted_at.is_(None))
    
    # 회원인 경우 자신의 데이터만, 비회원인 경우 세션별 데이터만
    if current_user:
        query = query.filter(UserCycle.user_id == current_user.id)
    else:
        query = query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    # 검색 조건
    if search:
        query = query.filter(
            or_(
                UserCycle.title.ilike(f"%{search}%"),
                UserCycle.description.ilike(f"%{search}%")
            )
        )
    
    # 전체 개수
    total = query.count()
    
    # 페이지네이션
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
    new_cycle = UserCycle(
        user_id=current_user.id if current_user else None,
        session_id=None if current_user else session_id,  # 회원이면 null, 비회원이면 세션 ID
        title=cycle_data.title,
        description=cycle_data.description,
        total_rounds=cycle_data.total_rounds,
        cycle_rest_seconds=cycle_data.cycle_rest_seconds
    )
    db.add(new_cycle)     # INSERT 쿼리가 "준비됨"
    db.commit()           # 실제 DB에 INSERT 실행됨
    db.refresh(new_cycle) # 새로 INSERT된 new_cycle의 ID 등 정보를 다시 로딩함
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
    query = db.query(UserCycle).filter(
            UserCycle.id == cycle_id,
            UserCycle.deleted_at.is_(None)
        )
    
    # 권한 확인
    if current_user:
        query = query.filter(
            or_(
                UserCycle.user_id == current_user.id,
                UserCycle.user_id.is_(None)
            )
        )
    else:
        query = query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found"
        )
    
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
    query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    # 권한 확인 (자신이 만든 사이클만 수정 가능)
    if current_user:
        query = query.filter(UserCycle.user_id == current_user.id)
    else:
        query = query.filter(
            UserCycle.user_id.is_(None), 
            UserCycle.session_id == session_id
        )
    
    cycle = query.first()
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found or no permission"
        )
    
    # 업데이트
    update_data = cycle_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cycle, field, value)
    
    db.commit()
    db.refresh(cycle)
    
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
    query = db.query(UserCycle).filter(
        UserCycle.id == cycle_id,
        UserCycle.deleted_at.is_(None)
    )
    
    # 권한 확인
    if current_user:
        query = query.filter(UserCycle.user_id == current_user.id)
    else:
        query = query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
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
    
    return ApiResponse(
        message="Cycle deleted successfully",
        data="Cycle has been deleted"
    )