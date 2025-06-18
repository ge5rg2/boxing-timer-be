from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.migration import (
    MigrationPreviewResponse,
    MigrationExecuteRequest, MigrationResultResponse,
    MigrationHistoryResponse, MigrationLogDetailResponse,
    CleanupResultResponse, MigrationStatsResponse
)
from app.schemas.response import ApiResponse
from app.services.guest_migration_service import GuestDataMigrationService
from app.dependencies import get_current_user_required

router = APIRouter()


@router.post("/preview", response_model=ApiResponse[MigrationPreviewResponse])
async def preview_migration_data(
    session_id: str = Header(..., alias="X-Session-ID"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    마이그레이션될 데이터 미리보기
    
    로그인한 사용자가 특정 세션 ID의 비회원 데이터를 미리 확인할 수 있습니다.
    """
    migration_service = GuestDataMigrationService(db)
    preview_data = migration_service.preview_migration_data(session_id)
    
    if "error" in preview_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to preview migration data: {preview_data['error']}"
        )
    
    return ApiResponse(
        message="Migration preview retrieved successfully",
        data=MigrationPreviewResponse(**preview_data)
    )


@router.post("/execute", response_model=ApiResponse[MigrationResultResponse])
async def execute_migration(
    request: MigrationExecuteRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    비회원 데이터를 현재 로그인한 계정으로 마이그레이션 실행
    
    지정된 세션 ID의 모든 비회원 데이터를 현재 사용자 계정으로 이전합니다.
    """
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Migration confirmation required"
        )
    
    migration_service = GuestDataMigrationService(db)
    
    try:
        # 미리보기로 데이터 존재 여부 확인
        preview = migration_service.preview_migration_data(request.session_id)
        if not preview.get("has_data", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No migration data found for the specified session"
            )
        
        # 마이그레이션 실행
        result = migration_service.migrate_guest_data_to_user(request.session_id, current_user)
        
        # 응답 데이터 구성
        success = len(result["errors"]) == 0
        total_migrated = (
            result["cycles_migrated"] + 
            result["combinations_migrated"] + 
            result["workout_logs_migrated"]
        )
        
        if success:
            message = f"Successfully migrated {total_migrated} items"
        elif total_migrated > 0:
            message = f"Partially migrated {total_migrated} items with some errors"
        else:
            message = "Migration failed"
        
        response_data = MigrationResultResponse(
            cycles_migrated=result["cycles_migrated"],
            combinations_migrated=result["combinations_migrated"],
            workout_logs_migrated=result["workout_logs_migrated"],
            errors=result["errors"],
            success=success,
            migration_log_id=result.get("migration_log_id"),
            message=message
        )
        
        return ApiResponse(
            message=message,
            data=response_data
        )
        
    except ValueError as e:
        # 이미 마이그레이션된 경우 등
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/history", response_model=ApiResponse[List[MigrationHistoryResponse]])
async def get_migration_history(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 마이그레이션 이력 조회
    
    현재 로그인한 사용자가 수행한 모든 마이그레이션 기록을 조회합니다.
    """
    migration_service = GuestDataMigrationService(db)
    history = migration_service.get_migration_history(current_user.id)
    
    return ApiResponse(
        message="Migration history retrieved successfully",
        data=[MigrationHistoryResponse(**item) for item in history]
    )


@router.get("/log/{migration_id}", response_model=ApiResponse[MigrationLogDetailResponse])
async def get_migration_log_detail(
    migration_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    특정 마이그레이션 로그 상세 조회
    
    마이그레이션 로그 ID로 해당 마이그레이션의 상세 정보를 조회합니다.
    """
    from app.models import MigrationLog
    
    migration_log = db.query(MigrationLog).filter(
        MigrationLog.id == migration_id,
        MigrationLog.user_id == current_user.id
    ).first()
    
    if not migration_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Migration log not found"
        )
    
    return ApiResponse(
        message="Migration log detail retrieved successfully",
        data=MigrationLogDetailResponse.model_validate(migration_log)
    )


# 관리자용 API들
@router.post("/cleanup", response_model=ApiResponse[CleanupResultResponse])
async def cleanup_old_guest_data(
    days_old: int = 30,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    오래된 비회원 데이터 정리 (관리자용)
    
    지정된 일수보다 오래된 비회원 데이터를 삭제합니다.
    보안상 일반 사용자는 사용할 수 없습니다.
    """
    # 관리자 권한 확인 (예시 - 실제로는 별도의 권한 시스템 구현 필요)
    if not current_user.email.endswith('@admin.com'):  # 임시 관리자 체크
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    if days_old < 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete data newer than 7 days"
        )
    
    migration_service = GuestDataMigrationService(db)
    result = migration_service.cleanup_old_guest_data(days_old)
    
    # 총 삭제 항목 수 계산
    total_deleted = (
        result["cycles_deleted"] + 
        result["combinations_deleted"] + 
        result["workout_logs_deleted"]
    )
    
    response_data = CleanupResultResponse(
        **result,
        total_deleted=total_deleted
    )
    
    return ApiResponse(
        message=f"Cleanup completed: {total_deleted} items deleted",
        data=response_data
    )


@router.get("/stats", response_model=ApiResponse[MigrationStatsResponse])
async def get_migration_stats(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    마이그레이션 통계 조회 (관리자용)
    
    전체 마이그레이션 통계 정보를 조회합니다.
    """
    # 관리자 권한 확인
    if not current_user.email.endswith('@admin.com'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    from app.models import MigrationLog
    from sqlalchemy import func
    
    # 기본 통계 조회
    total_migrations = db.query(MigrationLog).count()
    successful_migrations = db.query(MigrationLog).filter(
        MigrationLog.migration_status == "success"
    ).count()
    failed_migrations = db.query(MigrationLog).filter(
        MigrationLog.migration_status == "failed"
    ).count()
    partial_migrations = db.query(MigrationLog).filter(
        MigrationLog.migration_status == "partial"
    ).count()
    
    # 성공률 계산
    success_rate = (successful_migrations / total_migrations * 100) if total_migrations > 0 else 0
    
    # 평균 마이그레이션 수량 계산
    avg_stats = db.query(
        func.avg(MigrationLog.cycles_migrated).label('avg_cycles'),
        func.avg(MigrationLog.combinations_migrated).label('avg_combinations')
    ).filter(
        MigrationLog.migration_status.in_(["success", "partial"])
    ).first()
    
    average_cycles_migrated = float(avg_stats.avg_cycles or 0)
    average_combinations_migrated = float(avg_stats.avg_combinations or 0)
    
    # 가장 최근 마이그레이션 시간
    most_recent = db.query(func.max(MigrationLog.migration_started_at)).scalar()
    
    stats_data = MigrationStatsResponse(
        total_migrations=total_migrations,
        successful_migrations=successful_migrations,
        failed_migrations=failed_migrations,
        partial_migrations=partial_migrations,
        success_rate=round(success_rate, 2),
        average_cycles_migrated=round(average_cycles_migrated, 2),
        average_combinations_migrated=round(average_combinations_migrated, 2),
        most_recent_migration=most_recent
    )
    
    return ApiResponse(
        message="Migration statistics retrieved successfully",
        data=stats_data
    )


# 비회원을 위한 세션 정보 확인 API
@router.get("/session-info", response_model=ApiResponse[MigrationPreviewResponse])
async def get_session_info(
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """
    비회원 세션 정보 조회
    
    현재 세션에 저장된 데이터 정보를 조회합니다.
    비회원도 사용할 수 있습니다.
    """
    migration_service = GuestDataMigrationService(db)
    session_data = migration_service.preview_migration_data(session_id)
    
    if "error" in session_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve session info: {session_data['error']}"
        )
    
    return ApiResponse(
        message="Session information retrieved successfully",
        data=MigrationPreviewResponse(**session_data)
    )


# 회원가입 시 자동 마이그레이션을 위한 내부 API
@router.post("/auto-migrate", response_model=ApiResponse[MigrationResultResponse])
async def auto_migrate_on_signup(
    session_id: str = Header(..., alias="X-Session-ID"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    회원가입 시 자동 마이그레이션
    
    회원가입 직후 자동으로 호출되어 비회원 데이터를 이전합니다.
    내부적으로 사용되는 API입니다.
    """
    migration_service = GuestDataMigrationService(db)
    
    try:
        # 마이그레이션할 데이터가 있는지 확인
        preview = migration_service.preview_migration_data(session_id)
        if not preview.get("has_data", False):
            return ApiResponse(
                message="No data to migrate",
                data=MigrationResultResponse(
                    cycles_migrated=0,
                    combinations_migrated=0,
                    workout_logs_migrated=0,
                    errors=[],
                    success=True,
                    message="No data found to migrate"
                )
            )
        
        # 자동 마이그레이션 실행
        result = migration_service.migrate_guest_data_to_user(session_id, current_user)
        
        success = len(result["errors"]) == 0
        total_migrated = (
            result["cycles_migrated"] + 
            result["combinations_migrated"] + 
            result["workout_logs_migrated"]
        )
        
        message = f"Auto-migration completed: {total_migrated} items migrated"
        if not success:
            message += f" with {len(result['errors'])} errors"
        
        response_data = MigrationResultResponse(
            cycles_migrated=result["cycles_migrated"],
            combinations_migrated=result["combinations_migrated"],
            workout_logs_migrated=result["workout_logs_migrated"],
            errors=result["errors"],
            success=success,
            migration_log_id=result.get("migration_log_id"),
            message=message
        )
        
        return ApiResponse(
            message=message,
            data=response_data
        )
        
    except Exception as e:
        # 자동 마이그레이션 실패는 로그만 남기고 회원가입은 성공으로 처리
        print(f"Auto-migration failed for user {current_user.id}: {e}")
        
        return ApiResponse(
            message="Auto-migration failed, but signup completed successfully",
            data=MigrationResultResponse(
                cycles_migrated=0,
                combinations_migrated=0,
                workout_logs_migrated=0,
                errors=[str(e)],
                success=False,
                message="Auto-migration failed but account created successfully"
            )
        )