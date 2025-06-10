from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserCycle(Base):
    """사용자 정의 사이클 모델"""
    __tablename__ = "user_cycles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null 허용으로 비회원 지원
    title = Column(String(255), nullable=False)
    description = Column(Text)
    total_rounds = Column(Integer, nullable=False)
    usage_count = Column(Integer, nullable=True)
    cycle_rest_seconds = Column(Integer, default=60)  # 사이클 간 휴식 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # soft delete
    
    # 관계 설정
    user = relationship("User", back_populates="cycles")
    rounds = relationship("UserRound", back_populates="cycle", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="user_cycle")


class UserRound(Base):
    """사용자 정의 라운드 모델"""
    __tablename__ = "user_rounds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_cycle_id = Column(Integer, ForeignKey("user_cycles.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    rest_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계 설정
    cycle = relationship("UserCycle", back_populates="rounds")
    round_combinations = relationship("UserRoundCombination", back_populates="round", cascade="all, delete-orphan")


class UserRoundCombination(Base):
    """라운드 내 컴비네이션 실행 정보 모델"""
    __tablename__ = "user_round_combinations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_round_id = Column(Integer, ForeignKey("user_rounds.id"), nullable=False)
    user_combination_id = Column(Integer, ForeignKey("user_combinations.id"), nullable=False)
    start_time = Column(Integer, nullable=False)  # 라운드 시작 후 몇 초 뒤 실행
    duration = Column(Integer, nullable=False)
    execution_order = Column(Integer, nullable=False)  # 같은 시간대 컴비네이션 순서
    
    # 관계 설정
    round = relationship("UserRound", back_populates="round_combinations")
    combination = relationship("UserCombination", back_populates="round_combinations")


# 템플릿 시스템 (기본 제공, 프리미엄 전용)
class CycleTemplate(Base):
    """사이클 템플릿 모델"""
    __tablename__ = "cycle_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    total_rounds = Column(Integer, nullable=False)
    usage_count = Column(Integer, nullable=True)
    cycle_rest_seconds = Column(Integer, default=60)
    difficulty_level = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    category = Column(String(50))  # 'cardio', 'technique', 'power' 등
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_premium_only = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # soft delete
    
    # 관계 설정
    rounds = relationship("RoundTemplate", back_populates="cycle_template", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="cycle_template")


class RoundTemplate(Base):
    """라운드 템플릿 모델"""
    __tablename__ = "round_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_template_id = Column(Integer, ForeignKey("cycle_templates.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    rest_seconds = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 관계 설정
    cycle_template = relationship("CycleTemplate", back_populates="rounds")
    round_combinations = relationship("RoundTemplateCombination", back_populates="round_template", cascade="all, delete-orphan")


class RoundTemplateCombination(Base):
    """라운드 템플릿 내 컴비네이션 실행 정보 모델"""
    __tablename__ = "round_template_combinations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    round_template_id = Column(Integer, ForeignKey("round_templates.id"), nullable=False)
    combination_template_id = Column(Integer, ForeignKey("combination_templates.id"), nullable=False)
    start_time = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    execution_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 관계 설정
    round_template = relationship("RoundTemplate", back_populates="round_combinations")
    combination_template = relationship("CombinationTemplate", back_populates="round_combinations")