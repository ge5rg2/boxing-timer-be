from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 앱 기본 설정
    app_name: str = "Boxing Timer API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 데이터베이스 설정
    database_url: str = "postgresql://user:password@localhost/boxing_timer"
    
    # JWT 설정
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # CORS 설정
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # 파일 업로드 설정
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    # AWS S3 설정 (선택사항)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: Optional[str] = None
    
    # 외부 API 설정
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()