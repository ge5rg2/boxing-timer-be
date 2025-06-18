import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, UserCycle, CycleTemplate, WorkoutLog
from app.schemas.workout import (
    WorkoutStart, WorkoutComplete, WorkoutPause,
    WorkoutLogResponse, WorkoutHistoryResponse
)
from app.schemas.response import ApiResponse, PaginatedResponse, PaginationMeta
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/start", response_model=ApiResponse[WorkoutLogResponse])
async def start_workout(
    workout_data: WorkoutStart,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운동 세션 시작"""
    # 사이클 또는 템플릿 확인
    if workout_data.user_cycle_id and workout_data.cycle_template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify both user_cycle_id and cycle_template_id"
        )
    
    if not workout_data.user_cycle_id and not workout_data.cycle_template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either user_cycle_id or cycle_template_id"
        )
    
    total_rounds = 0
    
    # 사용자 사이클 확인
    if workout_data.user_cycle_id:
        cycle_query = db.query(UserCycle).filter(
            UserCycle.id == workout_data.user_cycle_id,
            UserCycle.deleted_at.is_(None)
        )
        
        if current_user:
            cycle_query = cycle_query.filter(
                or_(
                    UserCycle.user_id == current_user.id,
                    UserCycle.user_id.is_(None)
                )
            )
        else:
            cycle_query = cycle_query.filter(UserCycle.user_id.is_(None))
        
        cycle = cycle_query.first()
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User cycle not found"
            )
        total_rounds = cycle.total_rounds
    
    # 템플릿 사이클 확인
    if workout_data.cycle_template_id:
        template = db.query(CycleTemplate).filter(
            CycleTemplate.id == workout_data.cycle_template_id,
            CycleTemplate.is_active,
            CycleTemplate.deleted_at.is_(None)
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cycle template not found"
            )
        
        # 프리미엄 체크
        if template.is_premium_only and (not current_user or not current_user.is_premium):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium subscription required for this template"
            )
        
        total_rounds = template.total_rounds
    
    # 운동 로그 생성
    session_id = str(uuid.uuid4())
    workout_log = WorkoutLog(
        user_id=current_user.id if current_user else None,
        user_cycle_id=workout_data.user_cycle_id,
        cycle_template_id=workout_data.cycle_template_id,
        session_id=session_id,
        started_at=datetime.utcnow(),
        total_rounds=total_rounds,
        status="in_progress",
        device_info=workout_data.device_info
    )
    
    db.add(workout_log)
    db.commit()
    db.refresh(workout_log)
    
    return ApiResponse(
        message="Workout session started successfully",
        data=WorkoutLogResponse.model_validate(workout_log)
    )


@router.patch("/{session_id}/complete", response_model=ApiResponse[WorkoutLogResponse])
async def complete_workout(
    session_id: str,
    workout_data: WorkoutComplete,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운동 완료"""
    # 운동 세션 확인
    query = db.query(WorkoutLog).filter(WorkoutLog.session_id == session_id)
    
    if current_user:
        query = query.filter(
            or_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.user_id.is_(None)
            )
        )
    else:
        query = query.filter(WorkoutLog.user_id.is_(None))
    
    workout_log = query.first()
    if not workout_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    if workout_log.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workout already completed"
        )
    
    # 운동 완료 처리
    workout_log.completed_at = datetime.utcnow()
    workout_log.completed_rounds = workout_data.completed_rounds
    workout_log.status = "completed"
    
    # 사용 횟수 업데이트 (사용자 사이클의 경우)
    if workout_log.user_cycle_id:
        cycle = db.query(UserCycle).filter(UserCycle.id == workout_log.user_cycle_id).first()
        if cycle:
            cycle.usage_count = (cycle.usage_count or 0) + 1
    
    # 템플릿 사용 횟수 업데이트
    if workout_log.cycle_template_id:
        template = db.query(CycleTemplate).filter(CycleTemplate.id == workout_log.cycle_template_id).first()
        if template:
            template.usage_count = (template.usage_count or 0) + 1
    
    db.commit()
    db.refresh(workout_log)
    
    return ApiResponse(
        message="Workout completed successfully",
        data=WorkoutLogResponse.model_validate(workout_log)
    )


@router.patch("/{session_id}/pause", response_model=ApiResponse[WorkoutLogResponse])
async def pause_workout(
    session_id: str,
    workout_data: WorkoutPause,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """일시정지"""
    # 운동 세션 확인
    query = db.query(WorkoutLog).filter(WorkoutLog.session_id == session_id)
    
    if current_user:
        query = query.filter(
            or_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.user_id.is_(None)
            )
        )
    else:
        query = query.filter(WorkoutLog.user_id.is_(None))
    
    workout_log = query.first()
    if not workout_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    if workout_log.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pause active workout"
        )
    
    # 일시정지 처리
    workout_log.paused_duration_seconds += workout_data.paused_duration_seconds
    workout_log.status = "paused"
    
    db.commit()
    db.refresh(workout_log)
    
    return ApiResponse(
        message="Workout paused successfully",
        data=WorkoutLogResponse.model_validate(workout_log)
    )


@router.get("/history", response_model=PaginatedResponse[WorkoutHistoryResponse])
async def get_workout_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션 히스토리"""
    query = db.query(WorkoutLog)
    
    # 권한 확인
    if current_user:
        query = query.filter(
            or_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.user_id.is_(None)
            )
        )
    else:
        query = query.filter(WorkoutLog.user_id.is_(None))
    
    # 상태 필터
    if status:
        query = query.filter(WorkoutLog.status == status)
    
    # 전체 개수
    total = query.count()
    
    # 페이지네이션
    offset = (page - 1) * per_page
    workout_logs = query.order_by(WorkoutLog.started_at.desc()).offset(offset).limit(per_page).all()
    
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
        message="Workout history retrieved successfully",
        data=[WorkoutHistoryResponse.model_validate(log) for log in workout_logs],
        meta=meta
    )


@router.get("/{session_id}", response_model=ApiResponse[WorkoutLogResponse])
async def get_workout_detail(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """운동 세션 상세 조회"""
    query = db.query(WorkoutLog).filter(WorkoutLog.session_id == session_id)
    
    if current_user:
        query = query.filter(
            or_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.user_id.is_(None)
            )
        )
    else:
        query = query.filter(WorkoutLog.user_id.is_(None))
    
    workout_log = query.first()
    if not workout_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found"
        )
    
    return ApiResponse(
        message="Workout detail retrieved successfully",
        data=WorkoutLogResponse.model_validate(workout_log)
    )