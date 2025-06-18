from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.core.security import verify_token
from fastapi import Header

security = HTTPBearer(auto_error=False)

def get_session_id(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
) -> Optional[str]:
    """기기별 영구 세션 ID (만료 없음)"""
    
    # 세션 ID가 없으면 클라이언트에서 생성하도록 안내
    if not x_session_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "device_session_required",
                "message": "Please generate a device session ID in the app",
                "detail": "The X-Session-ID header is required for device-specific sessions"
            }
        )

    return x_session_id

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """현재 사용자 조회 (선택적 인증)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter(
        User.id == int(user_id),
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """현재 사용자 조회 (필수 인증)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_current_premium_user(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """프리미엄 사용자 확인"""
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required",
        )
    return current_user