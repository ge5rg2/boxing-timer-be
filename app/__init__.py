"""
Boxing Timer API Package

복싱 트레이닝을 위한 커스터마이징 타이머 앱의 백엔드 API
"""

__version__ = "1.0.0"
__author__ = "George"
__description__ = "Boxing Timer API for customized training sessions"

from .main import app
from .config import settings
from .database import get_db, create_tables

__all__ = ["app", "settings", "get_db", "create_tables"]