from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# OAuth 로그인 요청
class OAuthLoginRequest(BaseModel):
    provider: str = Field(..., description="OAuth 제공자", example="google")
    code: Optional[str] = Field(None, description="Authorization code")
    access_token: Optional[str] = Field(None, description="Access token (앱에서 직접 받은 경우)")
    id_token: Optional[str] = Field(None, description="ID token (Apple의 경우)")
    state: Optional[str] = Field(None, description="CSRF 방지용 state")


# OAuth 콜백 처리
class OAuthCallback(BaseModel):
    code: str = Field(..., description="Authorization code")
    state: Optional[str] = Field(None, description="State parameter")
    error: Optional[str] = Field(None, description="OAuth error")
    error_description: Optional[str] = Field(None, description="Error description")


# OAuth 사용자 정보
class OAuthUserInfo(BaseModel):
    provider_user_id: str
    email: Optional[str]
    name: Optional[str]
    profile_image_url: Optional[str]
    raw_data: Dict[str, Any]


# OAuth 계정 연결 응답
class OAuthAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_name: str
    email: Optional[str]
    name: Optional[str]
    profile_image_url: Optional[str]
    is_active: bool
    created_at: datetime
    


# OAuth 제공자 정보
class OAuthProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    display_name: str
    auth_url: Optional[str]
    is_active: bool



# 계정 연결 해제
class OAuthUnlinkRequest(BaseModel):
    provider: str = Field(..., description="연결 해제할 OAuth 제공자")


# Apple 로그인 특수 처리
class AppleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Apple ID token")
    authorization_code: str = Field(..., description="Apple authorization code")
    user_info: Optional[Dict[str, Any]] = Field(None, description="Apple user info (첫 로그인시)")


# 카카오 로그인
class KakaoLoginRequest(BaseModel):
    access_token: str = Field(..., description="카카오 액세스 토큰")


# 구글 로그인
class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token")


# OAuth URL 생성 요청
class OAuthURLRequest(BaseModel):
    provider: str = Field(..., description="OAuth 제공자")
    redirect_uri: str = Field(..., description="리다이렉트 URI")
    state: Optional[str] = Field(None, description="State parameter")


# OAuth URL 응답
class OAuthURLResponse(BaseModel):
    auth_url: str = Field(..., description="OAuth 인증 URL")
    state: Optional[str] = Field(None, description="State parameter")