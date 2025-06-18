from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# 마이그레이션 미리보기 요청
class MigrationPreviewRequest(BaseModel):
    session_id: str = Field(..., description="비회원 세션 ID")


# 마이그레이션 미리보기 응답
class MigrationPreviewResponse(BaseModel):
    cycles_count: int = Field(..., description="마이그레이션될 사이클 수")
    combinations_count: int = Field(..., description="마이그레이션될 컴비네이션 수") 
    workout_logs_count: int = Field(..., description="마이그레이션될 운동 기록 수")
    has_data: bool = Field(..., description="마이그레이션 가능한 데이터 존재 여부")
    preview: Optional[Dict[str, Any]] = Field(None, description="미리보기 상세 정보")


# 마이그레이션 실행 요청
class MigrationExecuteRequest(BaseModel):
    session_id: str = Field(..., description="비회원 세션 ID")
    confirm: bool = Field(default=True, description="마이그레이션 실행 확인")


# 마이그레이션 결과 응답
class MigrationResultResponse(BaseModel):
    cycles_migrated: int = Field(..., description="이전된 사이클 수")
    combinations_migrated: int = Field(..., description="이전된 컴비네이션 수")
    workout_logs_migrated: int = Field(..., description="이전된 운동 기록 수")
    errors: List[str] = Field(default=[], description="발생한 오류 목록")
    success: bool = Field(..., description="마이그레이션 성공 여부")
    migration_log_id: Optional[int] = Field(None, description="마이그레이션 로그 ID")
    message: str = Field(..., description="결과 메시지")


# 마이그레이션 이력 조회 응답
class MigrationHistoryResponse(BaseModel):
    id: int
    session_id: str
    cycles_migrated: int
    combinations_migrated: int
    workout_logs_migrated: int
    status: str = Field(..., description="success, partial, failed, in_progress")
    started_at: datetime
    completed_at: Optional[datetime]
    errors: List[str] = Field(default=[])
    
    model_config = ConfigDict(from_attributes=True)


# 마이그레이션 로그 상세 응답
class MigrationLogDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    user_id: int
    cycles_migrated: int
    combinations_migrated: int
    workout_logs_migrated: int
    migration_status: str
    error_details: Optional[str]
    migration_started_at: datetime
    migration_completed_at: Optional[datetime]
    created_at: datetime


# 데이터 정리 결과 응답
class CleanupResultResponse(BaseModel):
    cycles_deleted: int = Field(..., description="삭제된 사이클 수")
    combinations_deleted: int = Field(..., description="삭제된 컴비네이션 수")
    workout_logs_deleted: int = Field(..., description="삭제된 운동 기록 수")
    cutoff_date: datetime = Field(..., description="삭제 기준 날짜")
    total_deleted: int = Field(..., description="총 삭제된 항목 수")


# 마이그레이션 통계 응답
class MigrationStatsResponse(BaseModel):
    total_migrations: int = Field(..., description="총 마이그레이션 횟수")
    successful_migrations: int = Field(..., description="성공한 마이그레이션 횟수")
    failed_migrations: int = Field(..., description="실패한 마이그레이션 횟수")
    partial_migrations: int = Field(..., description="부분 성공한 마이그레이션 횟수")
    success_rate: float = Field(..., description="성공률 (0-100)")
    average_cycles_migrated: float = Field(..., description="평균 이전된 사이클 수")
    average_combinations_migrated: float = Field(..., description="평균 이전된 컴비네이션 수")
    most_recent_migration: Optional[datetime] = Field(None, description="가장 최근 마이그레이션 시간")