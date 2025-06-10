from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WorkoutLog(Base):
    """운동 로그 모델"""
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null 허용으로 비회원 지원
    user_cycle_id = Column(Integer, ForeignKey("user_cycles.id"), nullable=True)
    cycle_template_id = Column(Integer, ForeignKey("cycle_templates.id"), nullable=True)
    session_id = Column(String(100), nullable=False, index=True)  # 세션 식별용 UUID
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    paused_duration_seconds = Column(Integer, default=0)  # 일시정지 총 시간
    completed_rounds = Column(Integer, default=0)
    total_rounds = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # 'in_progress', 'completed', 'paused', 'stopped'
    device_info = Column(Text)  # 기기 정보 (선택사항)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 관계 설정
    user = relationship("User", back_populates="workout_logs")
    user_cycle = relationship("UserCycle", back_populates="workout_logs")
    cycle_template = relationship("CycleTemplate", back_populates="workout_logs")
    round_logs = relationship("WorkoutRoundLog", back_populates="workout_log", cascade="all, delete-orphan")


class WorkoutRoundLog(Base):
    """운동 라운드 로그 모델"""
    __tablename__ = "workout_round_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False)  # 'completed', 'skipped', 'stopped'
    actual_duration_seconds = Column(Integer)  # 실제 운동한 시간
    
    # 관계 설정
    workout_log = relationship("WorkoutLog", back_populates="round_logs")