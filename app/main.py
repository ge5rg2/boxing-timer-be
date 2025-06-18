from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import create_tables
from app.api import v1_router
from app.schemas.response import ErrorResponse

# FastAPI 앱 인스턴스 생성
print(settings.database_url)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="복싱 타이머 앱을 위한 RESTful API",
    debug=settings.debug
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    # 문자열 또는 dict인지 구분
    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("error", "http_exception")
        message = exc.detail.get("message", "Request failed")
        detail = exc.detail.get("detail")
    else:
        error_code = "http_exception"
        message = str(exc.detail)
        detail = None

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=message,
            error=error_code,
            detail=detail
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            error="An unexpected error occurred",
            detail=str(exc) if settings.debug else None
        ).dict()
    )

# 라우터 등록
app.include_router(v1_router, prefix="/api/v1")

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs"
    }

# 시작 시 데이터베이스 테이블 생성
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    create_tables()
    print(f"{settings.app_name} started successfully!")

# 종료 시 정리 작업
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    print(f"{settings.app_name} shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )