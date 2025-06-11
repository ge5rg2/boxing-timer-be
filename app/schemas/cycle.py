from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 라운드 생성/업데이트
class RoundCreate(BaseModel):
    round_number: int = Field(..., ge=1)
    duration_seconds: int = Field(..., ge=1)
    rest_seconds: int = Field(..., ge=0)


class RoundUpdate(BaseModel):
    duration_seconds: Optional[int] = Field(None, ge=1)
    rest_seconds: Optional[int] = Field(None, ge=0)


# 라운드 응답
class RoundResponse(BaseModel):
    id: int
    round_number: int
    duration_seconds: int
    rest_seconds: int
    created_at: datetime
    
    class Config:
        from_attributes = True


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
    id: int
    user_combination_id: int
    start_time: int
    duration: int
    execution_order: int
    
    class Config:
        from_attributes = True


# 사이클 생성
class CycleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    total_rounds: int = Field(..., ge=1)
    cycle_rest_seconds: int = Field(default=60, ge=0)


# 사이클 업데이트
class CycleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    total_rounds: Optional[int] = Field(None, ge=1)
    cycle_rest_seconds: Optional[int] = Field(None, ge=0)


# 사이클 응답 (라운드 포함)
class CycleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    usage_count: Optional[int]
    cycle_rest_seconds: int
    created_at: datetime
    updated_at: datetime
    rounds: List[RoundResponse] = []
    
    class Config:
        from_attributes = True


# 사이클 목록 응답 (간단 버전)
class CycleListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    usage_count: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# 템플릿 응답
class CycleTemplateResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    total_rounds: int
    cycle_rest_seconds: int
    difficulty_level: str
    category: Optional[str]
    is_premium_only: bool
    
    class Config:
        from_attributes = True