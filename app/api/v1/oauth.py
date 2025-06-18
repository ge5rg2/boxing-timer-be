from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OAuthProvider, UserOAuthAccount
from app.schemas import (
    GoogleLoginRequest, KakaoLoginRequest, AppleLoginRequest,
    OAuthAccountResponse, OAuthProviderResponse, OAuthUnlinkRequest,
    OAuthURLRequest, OAuthURLResponse
)
from app.schemas.user import TokenResponse, UserResponse
from app.schemas.response import ApiResponse
from app.services.oauth_service import OAuthService
from app.core.security import create_access_token
from app.dependencies import get_current_user_required
from app.config import settings

router = APIRouter()


@router.get("/providers", response_model=ApiResponse[List[OAuthProviderResponse]])
async def get_oauth_providers(db: Session = Depends(get_db)):
    """사용 가능한 OAuth 제공자 목록 조회"""
    providers = db.query(OAuthProvider).filter(OAuthProvider.is_active).all()
    
    return ApiResponse(
        message="OAuth providers retrieved successfully",
        data=[OAuthProviderResponse.from_orm(provider) for provider in providers]
    )


@router.post("/google/login", response_model=ApiResponse[TokenResponse])
async def google_login(
    login_data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Google OAuth 로그인"""
    oauth_service = OAuthService(db)
    
    # Google 제공자 확인
    provider = await oauth_service.get_provider("google")
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth not configured"
        )
    
    # Google 사용자 정보 조회
    oauth_info = await oauth_service.get_oauth_user_info(
        provider, None, login_data.id_token
    )
    
    if not oauth_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Google"
        )
    
    # 사용자 찾기 또는 생성
    user, is_new_user = await oauth_service.find_or_create_user(oauth_info, provider)
    
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
    
    message = "User registered successfully" if is_new_user else "Login successful"
    
    return ApiResponse(
        message=message,
        data=token_response
    )


@router.post("/kakao/login", response_model=ApiResponse[TokenResponse])
async def kakao_login(
    login_data: KakaoLoginRequest,
    db: Session = Depends(get_db)
):
    """카카오 OAuth 로그인"""
    oauth_service = OAuthService(db)
    
    # 카카오 제공자 확인
    provider = await oauth_service.get_provider("kakao")
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kakao OAuth not configured"
        )
    
    # 카카오 사용자 정보 조회
    oauth_info = await oauth_service.get_oauth_user_info(
        provider, login_data.access_token
    )
    
    if not oauth_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Kakao"
        )
    
    # 사용자 찾기 또는 생성
    user, is_new_user = await oauth_service.find_or_create_user(oauth_info, provider)
    
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
    
    message = "User registered successfully" if is_new_user else "Login successful"
    
    return ApiResponse(
        message=message,
        data=token_response
    )


@router.post("/apple/login", response_model=ApiResponse[TokenResponse])
async def apple_login(
    login_data: AppleLoginRequest,
    db: Session = Depends(get_db)
):
    """Apple OAuth 로그인"""
    oauth_service = OAuthService(db)
    
    # Apple 제공자 확인
    provider = await oauth_service.get_provider("apple")
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apple OAuth not configured"
        )
    
    # Apple 사용자 정보 조회
    oauth_info = await oauth_service.get_oauth_user_info(
        provider, None, login_data.id_token
    )
    
    if not oauth_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Apple"
        )
    
    # Apple의 경우 첫 로그인시 추가 정보가 있을 수 있음
    if login_data.user_info:
        oauth_info.name = login_data.user_info.get("name", {}).get("firstName", "") + " " + \
                         login_data.user_info.get("name", {}).get("lastName", "")
        oauth_info.email = login_data.user_info.get("email", oauth_info.email)
    
    # 사용자 찾기 또는 생성
    user, is_new_user = await oauth_service.find_or_create_user(oauth_info, provider)
    
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
    
    message = "User registered successfully" if is_new_user else "Login successful"
    
    return ApiResponse(
        message=message,
        data=token_response
    )


@router.get("/accounts", response_model=ApiResponse[List[OAuthAccountResponse]])
async def get_oauth_accounts(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """현재 사용자의 연결된 OAuth 계정 목록"""
    oauth_accounts = db.query(UserOAuthAccount).join(OAuthProvider).filter(
        UserOAuthAccount.user_id == current_user.id,
        UserOAuthAccount.is_active
    ).all()
    
    return ApiResponse(
        message="OAuth accounts retrieved successfully",
        data=[
            OAuthAccountResponse(
                id=account.id,
                provider_name=account.provider.display_name,
                email=account.email,
                name=account.name,
                profile_image_url=account.profile_image_url,
                is_active=account.is_active,
                created_at=account.created_at
            ) for account in oauth_accounts
        ]
    )


@router.post("/unlink", response_model=ApiResponse[str])
async def unlink_oauth_account(
    unlink_data: OAuthUnlinkRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """OAuth 계정 연결 해제"""
    oauth_service = OAuthService(db)
    
    try:
        success = await oauth_service.unlink_oauth_account(current_user, unlink_data.provider)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OAuth account not found"
            )
        
        return ApiResponse(
            message="OAuth account unlinked successfully",
            data="Account has been unlinked"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auth-url", response_model=ApiResponse[OAuthURLResponse])
async def get_oauth_auth_url(
    url_request: OAuthURLRequest,
    db: Session = Depends(get_db)
):
    """OAuth 인증 URL 생성 (웹 버전용)"""
    oauth_service = OAuthService(db)
    
    provider = await oauth_service.get_provider(url_request.provider)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    auth_url = oauth_service.generate_oauth_url(
        provider, 
        url_request.redirect_uri, 
        url_request.state
    )
    
    return ApiResponse(
        message="OAuth URL generated successfully",
        data=OAuthURLResponse(
            auth_url=auth_url,
            state=url_request.state
        )
    )


# 계정 연결 (기존 사용자가 추가 OAuth 계정 연결)
@router.post("/link/{provider_name}", response_model=ApiResponse[OAuthAccountResponse])
async def link_oauth_account(
    provider_name: str,
    login_data: dict,  # 제공자별로 다른 데이터 형식
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """기존 사용자에게 OAuth 계정 연결"""
    oauth_service = OAuthService(db)
    
    provider = await oauth_service.get_provider(provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth provider not found"
        )
    
    # 기존 연결 확인
    existing_account = db.query(UserOAuthAccount).filter(
        UserOAuthAccount.user_id == current_user.id,
        UserOAuthAccount.provider_id == provider.id,
        UserOAuthAccount.is_active
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth account already linked"
        )
    
    # OAuth 사용자 정보 조회
    if provider_name == "google":
        oauth_info = await oauth_service.get_oauth_user_info(
            provider, None, login_data.get("id_token")
        )
    elif provider_name == "kakao":
        oauth_info = await oauth_service.get_oauth_user_info(
            provider, login_data.get("access_token")
        )
    elif provider_name == "apple":
        oauth_info = await oauth_service.get_oauth_user_info(
            provider, None, login_data.get("id_token")
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported provider"
        )
    
    if not oauth_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from OAuth provider"
        )
    
    # 다른 사용자가 이미 이 OAuth 계정을 사용하고 있는지 확인
    existing_oauth = db.query(UserOAuthAccount).filter(
        UserOAuthAccount.provider_id == provider.id,
        UserOAuthAccount.provider_user_id == oauth_info.provider_user_id,
        UserOAuthAccount.is_active
    ).first()
    
    if existing_oauth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This OAuth account is already linked to another user"
        )
    
    # OAuth 계정 연결
    oauth_service._create_oauth_account(current_user, provider, oauth_info)
    
    # 새로 생성된 계정 정보 반환
    new_account = db.query(UserOAuthAccount).filter(
        UserOAuthAccount.user_id == current_user.id,
        UserOAuthAccount.provider_id == provider.id,
        UserOAuthAccount.provider_user_id == oauth_info.provider_user_id
    ).first()
    
    return ApiResponse(
        message="OAuth account linked successfully",
        data=OAuthAccountResponse(
            id=new_account.id,
            provider_name=provider.display_name,
            email=new_account.email,
            name=new_account.name,
            profile_image_url=new_account.profile_image_url,
            is_active=new_account.is_active,
            created_at=new_account.created_at
        )
    )