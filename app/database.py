from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


# 데이터베이스 세션 의존성
def get_db():
    """데이터베이스 세션을 생성하고 반환"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 데이터베이스 테이블 생성
def create_tables():
    """모든 테이블을 생성"""
    Base.metadata.create_all(bind=engine)