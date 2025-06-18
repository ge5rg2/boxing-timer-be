"""
API Package

FastAPI 라우터들과 API 관련 의존성들을 관리
"""

from .v1 import router as v1_router

__all__ = ["v1_router"]