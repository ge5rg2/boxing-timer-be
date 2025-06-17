from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.response import ApiResponse
from app.dependencies import get_current_user_required

router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user_required)):
    """현재 사용자 정보 조회"""
    return ApiResponse(
        message="User information retrieved successfully",
        data=UserResponse.model_validate(current_user)
    )


@router.patch("/{member_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    member_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """사용자 정보 업데이트"""
    # 자신의 정보만 수정 가능
    if current_user.id != member_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile"
        )
    
    # 이메일 중복 확인 (변경하는 경우)
    if user_data.email and user_data.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != current_user.id,
            User.deleted_at.is_(None)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        current_user.email = user_data.email
    
    db.commit()
    db.refresh(current_user)
    
    return ApiResponse(
        message="User information updated successfully",
        data=UserResponse.model_validate(current_user)
    )