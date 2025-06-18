from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 방식
    
    id: int
    email: str
    name: Optional[str] = None                
    profile_image_url: Optional[str] = None   
    is_premium: bool
    is_email_verified: bool                   
    signup_method: str                        
    created_at: datetime
    updated_at: datetime
    


# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 구독 정보
class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan_type: str
    started_at: datetime
    expires_at: Optional[datetime]
    status: str
