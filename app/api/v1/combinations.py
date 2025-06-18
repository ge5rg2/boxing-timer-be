from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, UserCombination, UserRound, UserRoundCombination, UserCycle
from app.schemas.combination import (
    CombinationCreate, CombinationUpdate, CombinationResponse
)
from app.schemas.cycle import (
    RoundCombinationCreate, RoundCombinationResponse
)
from app.schemas.response import ApiResponse, PaginatedResponse, PaginationMeta
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CombinationResponse])
async def get_combinations(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 컴비네이션 전체 보기"""
    query = db.query(UserCombination).filter(UserCombination.deleted_at.is_(None))
    
    # 권한 확인
    if current_user:
        query = query.filter(UserCombination.user_id == current_user.id)
    else:
        query = query.filter(UserCombination.user_id.is_(None))
    
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
    
    return PaginatedResponse(
        message="Combinations retrieved successfully",
        data=[CombinationResponse.from_orm(combo) for combo in combinations],
        meta=meta
    )


@router.post("/", response_model=ApiResponse[CombinationResponse])
async def create_combination(
    combination_data: CombinationCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 컴비네이션 등록"""
    new_combination = UserCombination(
        user_id=current_user.id if current_user else None,
        title=combination_data.title,
        description=combination_data.description,
        audio_url=combination_data.audio_url,
        audio_duration_seconds=combination_data.audio_duration_seconds,
        audio_file_size=combination_data.audio_file_size
    )
    
    db.add(new_combination)
    db.commit()
    db.refresh(new_combination)
    
    return ApiResponse(
        message="Combination created successfully",
        data=CombinationResponse.from_orm(new_combination)
    )


@router.patch("/{combination_id}", response_model=ApiResponse[CombinationResponse])
async def update_combination(
    combination_id: int,
    combination_data: CombinationUpdate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """컴비네이션 수정"""
    query = db.query(UserCombination).filter(
        UserCombination.id == combination_id,
        UserCombination.deleted_at.is_(None)
    )
    
    # 권한 확인
    if current_user:
        query = query.filter(UserCombination.user_id == current_user.id)
    else:
        query = query.filter(UserCombination.user_id.is_(None))
    
    combination = query.first()
    if not combination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combination not found or no permission"
        )
    
    # 업데이트
    update_data = combination_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(combination, field, value)
    
    db.commit()
    db.refresh(combination)
    
    return ApiResponse(
        message="Combination updated successfully",
        data=CombinationResponse.from_orm(combination)
    )


@router.delete("/{combination_id}", response_model=ApiResponse[str])
async def delete_combination(
    combination_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """컴비네이션 삭제 (소프트 삭제)"""
    query = db.query(UserCombination).filter(
        UserCombination.id == combination_id,
        UserCombination.deleted_at.is_(None)
    )
    
    # 권한 확인
    if current_user:
        query = query.filter(UserCombination.user_id == current_user.id)
    else:
        query = query.filter(UserCombination.user_id.is_(None))
    
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
    
    return ApiResponse(
        message="Combination deleted successfully",
        data="Combination has been deleted"
    )


# 라운드 컴비네이션 관리 엔드포인트
@router.get("/rounds/{round_id}/combinations", response_model=ApiResponse[List[RoundCombinationResponse]])
async def get_round_combinations(
    round_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """해당 라운드 내 컴비네이션 목록"""
    # 라운드 권한 확인
    round_query = db.query(UserRound).join(UserCycle).filter(
        UserRound.id == round_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        round_query = round_query.filter(
            or_(
                UserCycle.user_id == current_user.id,
                UserCycle.user_id.is_(None)
            )
        )
    else:
        round_query = round_query.filter(UserCycle.user_id.is_(None))
    
    round_obj = round_query.first()
    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found"
        )
    
    # 라운드 컴비네이션 조회
    round_combinations = db.query(UserRoundCombination).filter(
        UserRoundCombination.user_round_id == round_id
    ).order_by(UserRoundCombination.start_time, UserRoundCombination.execution_order).all()
    
    return ApiResponse(
        message="Round combinations retrieved successfully",
        data=[RoundCombinationResponse.from_orm(rc) for rc in round_combinations]
    )


@router.post("/rounds/{round_id}/combinations", response_model=ApiResponse[RoundCombinationResponse])
async def add_round_combination(
    round_id: int,
    combination_data: RoundCombinationCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """컴비네이션 추가 (start_time, duration 등 포함)"""
    # 라운드 권한 확인
    round_query = db.query(UserRound).join(UserCycle).filter(
        UserRound.id == round_id,
        UserCycle.deleted_at.is_(None)
    )
    
    if current_user:
        round_query = round_query.filter(UserCycle.user_id == current_user.id)
    else:
        round_query = round_query.filter(UserCycle.user_id.is_(None))
    
    round_obj = round_query.first()
    if not round_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found or no permission"
        )
    
    # 컴비네이션 존재 확인
    combination = db.query(UserCombination).filter(
        UserCombination.id == combination_data.user_combination_id,
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
        user_combination_id=combination_data.user_combination_id,
        start_time=combination_data.start_time,
        duration=combination_data.duration,
        execution_order=combination_data.execution_order
    )
    
    db.add(new_round_combination)
    db.commit()
    db.refresh(new_round_combination)
    
    return ApiResponse(
        message="Round combination added successfully",
        data=RoundCombinationResponse.from_orm(new_round_combination)
    )