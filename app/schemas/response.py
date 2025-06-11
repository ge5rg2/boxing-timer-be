from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')
# RES wrapper for API responses

class ApiResponse(BaseModel, Generic[T]):
    """API 응답 공통 모델"""
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error: Optional[str] = None


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답 모델"""
    success: bool = True
    message: str = "Success"
    data: list[T] = []
    meta: PaginationMeta
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    success: bool = False
    message: str
    error: str
    detail: Optional[Any] = None