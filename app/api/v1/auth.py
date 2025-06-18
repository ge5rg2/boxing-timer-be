from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserRegister, UserLogin, PasswordChange, TokenResponse, UserResponse
from app.schemas.response import ApiResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user_required
from app.services.guest_migration_service import GuestDataMigrationService
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(
    user_data: UserRegister, 
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db)
):
    """사용자 등록 (비회원 데이터 자동 마이그레이션 포함)"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.deleted_at.is_(None)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        signup_method="email",
        is_email_verified=False  # 실제로는 이메일 인증 프로세스 필요
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 비회원 데이터 자동 마이그레이션
    migration_result = None
    migration_message = ""
    
    if session_id:
        try:
            migration_service = GuestDataMigrationService(db)
            
            # 마이그레이션할 데이터가 있는지 확인
            preview = migration_service.preview_migration_data(session_id)
            if preview.get("has_data", False):
                migration_result = migration_service.migrate_guest_data_to_user(session_id, new_user)
                
                total_migrated = (
                    migration_result["cycles_migrated"] + 
                    migration_result["combinations_migrated"] + 
                    migration_result["workout_logs_migrated"]
                )
                
                if total_migrated > 0:
                    migration_message = f" ({total_migrated}개 데이터 자동 이전)"
                    
        except Exception as e:
            # 마이그레이션 실패해도 회원가입은 성공으로 처리
            print(f"Migration failed during registration for user {new_user.id}: {e}")
            migration_message = " (데이터 이전 실패)"
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=access_token_expires
    )
    
    token_response = TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )
    
    message = f"User registered successfully{migration_message}"
    
    return ApiResponse(
        message=message,
        data=token_response
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """사용자 로그인"""
    # 사용자 확인
    user = db.query(User).filter(
        User.email == user_data.email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    token_response = TokenResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )
    
    return ApiResponse(
        message="Login successful",
        data=token_response
    )


@router.post("/change-password", response_model=ApiResponse[str])
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """비밀번호 변경"""
    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # 새 비밀번호로 업데이트
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return ApiResponse(
        message="Password changed successfully",
        data="Password updated"
    )


@router.post("/logout", response_model=ApiResponse[str])
async def logout(current_user: User = Depends(get_current_user_required)):
    """로그아웃 (클라이언트에서 토큰 삭제 처리)"""
    return ApiResponse(
        message="Logged out successfully",
        data="Please remove the token from client storage"
    )