from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class OAuthProvider(Base):
    """OAuth 제공자 정보"""
    __tablename__ = "oauth_providers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # 'google', 'kakao', 'apple'
    display_name = Column(String(100), nullable=False)  # 'Google', '카카오톡', 'Apple'
    client_id = Column(String(255))
    client_secret = Column(Text)  # Apple의 경우 private key
    auth_url = Column(String(500))
    token_url = Column(String(500))
    user_info_url = Column(String(500))
    scope = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 관계 설정
    user_accounts = relationship("UserOAuthAccount", back_populates="provider")


class UserOAuthAccount(Base):
    """사용자 OAuth 계정 연결 정보"""
    __tablename__ = "user_oauth_accounts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("oauth_providers.id"), nullable=False)
    provider_user_id = Column(String(255), nullable=False)  # OAuth 제공자의 사용자 ID
    email = Column(String(255))  # OAuth에서 제공하는 이메일
    name = Column(String(255))   # OAuth에서 제공하는 이름
    profile_image_url = Column(String(500))  # 프로필 이미지 URL
    access_token = Column(Text)  # 암호화 저장 권장
    refresh_token = Column(Text)  # 암호화 저장 권장
    token_expires_at = Column(DateTime(timezone=True))
    raw_data = Column(Text)  # JSON 형태로 원본 데이터 저장
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 관계 설정
    user = relationship("User", back_populates="oauth_accounts")
    provider = relationship("OAuthProvider", back_populates="user_accounts")
    
    # 복합 유니크 인덱스 (한 제공자당 하나의 계정만)
    __table_args__ = (
        {"extend_existing": True}
    )