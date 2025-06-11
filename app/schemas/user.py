from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# 사용자 등록
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


# 사용자 로그인
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 비밀번호 변경
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# 사용자 정보 업데이트
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


# 사용자 응답 모델
class UserResponse(BaseModel):
    id: int
    email: str
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 구독 정보
class SubscriptionResponse(BaseModel):
    id: int
    plan_type: str
    started_at: datetime
    expires_at: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True