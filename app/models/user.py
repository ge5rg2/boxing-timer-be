from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # OAuth 사용자는 null 가능
    name = Column(String(255))  # 이름 추가
    profile_image_url = Column(String(500))  # 프로필 이미지
    signup_method = Column(String(20), default='email')  # 가입 방법 구분
    is_email_verified = Column(Boolean, default=False)  # 이메일 인증 여부
    oauth_accounts = relationship("UserOAuthAccount")  # OAuth 계정 연결
    is_premium = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # 관계 설정
    cycles = relationship("UserCycle", back_populates="user")
    combinations = relationship("UserCombination", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    workout_logs = relationship("WorkoutLog", back_populates="user")


class Subscription(Base):
    """구독 정보 모델"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan_type = Column(String(50), nullable=False)  # 'monthly', 'yearly', 'lifetime'
    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # lifetime의 경우 null
    paid_at = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    status = Column(String(20), nullable=False)  # 'active', 'cancelled', 'expired', 'pending'
    payment_method = Column(String(50))  # 'card', 'paypal', 'apple_pay', 'google_pay'
    transaction_id = Column(String(255))  # 결제 시스템의 트랜잭션 ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 관계 설정
    user = relationship("User", back_populates="subscriptions")