from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MigrationLog(Base):
    """마이그레이션 로그 모델"""
    __tablename__ = "migration_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)  # 마이그레이션된 세션 ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 마이그레이션 대상 사용자
    cycles_migrated = Column(Integer, default=0)
    combinations_migrated = Column(Integer, default=0)
    workout_logs_migrated = Column(Integer, default=0)
    migration_status = Column(String(20), nullable=False)  # 'success', 'partial', 'failed', 'in_progress'
    error_details = Column(Text)  # 오류 상세 내용 (JSON 형태)
    migration_started_at = Column(DateTime(timezone=True), nullable=False)
    migration_completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계 설정
    user = relationship("User", back_populates="migration_logs")