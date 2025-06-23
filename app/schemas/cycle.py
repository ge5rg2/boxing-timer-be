from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# 라운드 생성/업데이트
class RoundCreate(BaseModel):
    round_number: int = Field(..., ge=1)
    duration_seconds: int = Field(default=180, ge=30, le=600)  # 최소 30초, 최대 10분
    rest_seconds: int = Field(default=60, ge=30, le=300)  # 최소 30초, 최대 5분


class RoundUpdate(BaseModel):
    duration_seconds: Optional[int] = Field(None, ge=30, le=600)
    rest_seconds: Optional[int] = Field(None, ge=30, le=300)


# 라운드 응답
class RoundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    round_number: int
    duration_seconds: int
    rest_seconds: int
    created_at: datetime
    


# 라운드 컴비네이션 생성/업데이트
class RoundCombinationCreate(BaseModel):
    user_combination_id: int
    start_time: int = Field(..., ge=0)
    duration: int = Field(..., ge=1)
    execution_order: int = Field(..., ge=1)


class RoundCombinationUpdate(BaseModel):
    start_time: Optional[int] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=1)
    execution_order: Optional[int] = Field(None, ge=1)


# 라운드 컴비네이션 응답
class RoundCombinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_combination_id: int
    start_time: int
    duration: int
    execution_order: int
    


# 사이클 생성
class CycleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    total_rounds: int = Field(default=3, ge=1, le=20) # 최대 20라운드
    cycle_rest_seconds: int = Field(default=60, ge=0, le=600) # 최대 10분 휴식
    cycle_count: int = Field(default=1, ge=1, le=10)  # 사이클 실행 횟수 (최대 10회)


# 사이클 업데이트
class CycleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    total_rounds: Optional[int] = Field(None, ge=1, le=20)
    cycle_rest_seconds: Optional[int] = Field(None, ge=0, le=600)
    cycle_count: int = Field(None, ge=1, le=10)  # 사이클 실행 횟수 (최대 10회)


# 사이클 응답 (라운드 포함)
class CycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    usage_count: Optional[int]
    cycle_count: int
    cycle_rest_seconds: int
    created_at: datetime
    updated_at: datetime
    rounds: List[RoundResponse] = []
    



# 사이클 목록 응답 (간단 버전)
class CycleListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    usage_count: Optional[int]
    created_at: datetime
    



# 템플릿 응답
class CycleTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    cycle_count: int
    cycle_rest_seconds: int
    difficulty_level: str
    category: Optional[str]
    is_premium_only: bool
