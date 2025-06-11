from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 운동 세션 시작
class WorkoutStart(BaseModel):
    user_cycle_id: Optional[int] = None
    cycle_template_id: Optional[int] = None
    device_info: Optional[str] = None


# 운동 세션 완료
class WorkoutComplete(BaseModel):
    completed_rounds: int = Field(..., ge=0)


# 운동 세션 일시정지
class WorkoutPause(BaseModel):
    paused_duration_seconds: int = Field(..., ge=0)


# 라운드 로그 응답
class WorkoutRoundLogResponse(BaseModel):
    id: int
    round_number: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    actual_duration_seconds: Optional[int]
    
    class Config:
        from_attributes = True


# 운동 로그 응답
class WorkoutLogResponse(BaseModel):
    id: int
    session_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    paused_duration_seconds: int
    completed_rounds: int
    total_rounds: int
    status: str
    device_info: Optional[str]
    round_logs: List[WorkoutRoundLogResponse] = []
    
    class Config:
        from_attributes = True


# 운동 히스토리 응답 (간단 버전)
class WorkoutHistoryResponse(BaseModel):
    id: int
    session_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    completed_rounds: int
    total_rounds: int
    status: str
    
    class Config:
        from_attributes = True