from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# 컴비네이션 생성
class CombinationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None # Nullable
    audio_url: Optional[str] = Field(None, max_length=500)
    audio_duration_seconds: Optional[int] = Field(None, ge=0)
    audio_file_size: Optional[int] = Field(None, ge=0)


# 컴비네이션 업데이트
class CombinationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)
    audio_duration_seconds: Optional[int] = Field(None, ge=0)
    audio_file_size: Optional[int] = Field(None, ge=0)


# 컴비네이션 응답
class CombinationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    audio_url: Optional[str]
    audio_duration_seconds: Optional[int]
    audio_file_size: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 컴비네이션 템플릿 응답
class CombinationTemplateResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    audio_url: Optional[str]
    audio_duration_seconds: Optional[int]
    category: Optional[str]
    difficulty_level: str
    
    class Config:
        from_attributes = True