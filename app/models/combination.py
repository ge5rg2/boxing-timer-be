from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserCombination(Base):
    """사용자 정의 컴비네이션 모델"""
    __tablename__ = "user_combinations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null 허용으로 비회원 지원
    title = Column(String(255), nullable=False)
    description = Column(Text)
    session_id = Column(String(100), nullable=True, index=True)  # ✅ 추가
    audio_url = Column(String(500))
    audio_duration_seconds = Column(Integer)  # 음성 파일 길이
    audio_file_size = Column(Integer)  # 파일 크기 (bytes)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # soft delete
    
    # 관계 설정
    user = relationship("User", back_populates="combinations")
    round_combinations = relationship("UserRoundCombination", back_populates="combination")


class CombinationTemplate(Base):
    """컴비네이션 템플릿 모델 (기본 제공, 프리미엄 전용)"""
    __tablename__ = "combination_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    audio_url = Column(String(500))
    audio_duration_seconds = Column(Integer)
    audio_file_size = Column(Integer)
    category = Column(String(50))  # 'jab', 'cross', 'hook', 'uppercut', 'combo' 등
    difficulty_level = Column(String(20), default='beginner')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # soft delete
    
    # 관계 설정
    round_combinations = relationship("RoundTemplateCombination", back_populates="combination_template")