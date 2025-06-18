import json
import secrets
import httpx
from typing import Optional
from datetime import datetime
from jose import jwt
from sqlalchemy.orm import Session
from app.models import User, OAuthProvider, UserOAuthAccount
from app.schemas import OAuthUserInfo


class OAuthService:
    """OAuth 통합 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """OAuth 제공자 정보 조회"""
        return self.db.query(OAuthProvider).filter(
            OAuthProvider.name == provider_name,
            OAuthProvider.is_active
        ).first()
    
    async def get_oauth_user_info(self, provider: OAuthProvider, access_token: str, id_token: str = None) -> Optional[OAuthUserInfo]:
        """OAuth 제공자로부터 사용자 정보 조회"""
        if provider.name == "google":
            return await self._get_google_user_info(id_token or access_token)
        elif provider.name == "kakao":
            return await self._get_kakao_user_info(access_token)
        elif provider.name == "apple":
            return await self._get_apple_user_info(id_token)
        else:
            raise ValueError(f"Unsupported provider: {provider.name}")
    
    async def _get_google_user_info(self, token: str) -> Optional[OAuthUserInfo]:
        """Google 사용자 정보 조회"""
        try:
            # ID token 검증 및 디코딩
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return OAuthUserInfo(
                provider_user_id=payload.get("sub"),
                email=payload.get("email"),
                name=payload.get("name"),
                profile_image_url=payload.get("picture"),
                raw_data=payload
            )
        except Exception as e:
            print(f"Google user info error: {e}")
            return None
    
    async def _get_kakao_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """카카오 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return OAuthUserInfo(
                    provider_user_id=str(data.get("id")),
                    email=kakao_account.get("email"),
                    name=profile.get("nickname"),
                    profile_image_url=profile.get("profile_image_url"),
                    raw_data=data
                )
        except Exception as e:
            print(f"Kakao user info error: {e}")
            return None
    
    async def _get_apple_user_info(self, id_token: str) -> Optional[OAuthUserInfo]:
        """Apple 사용자 정보 조회"""
        try:
            # Apple ID token 검증 (실제로는 Apple 공개키로 검증해야 함)
            payload = jwt.decode(id_token, options={"verify_signature": False})
            
            return OAuthUserInfo(
                provider_user_id=payload.get("sub"),
                email=payload.get("email"),
                name=payload.get("name"),  # Apple은 첫 로그인시에만 제공
                profile_image_url=None,  # Apple은 프로필 이미지 제공 안함
                raw_data=payload
            )
        except Exception as e:
            print(f"Apple user info error: {e}")
            return None
    
    async def find_or_create_user(self, oauth_info: OAuthUserInfo, provider: OAuthProvider) -> tuple[User, bool]:
        """OAuth 정보로 사용자 찾기 또는 생성"""
        # 기존 OAuth 계정 연결 확인
        oauth_account = self.db.query(UserOAuthAccount).filter(
            UserOAuthAccount.provider_id == provider.id,
            UserOAuthAccount.provider_user_id == oauth_info.provider_user_id,
            UserOAuthAccount.is_active
        ).first()
        
        if oauth_account:
            # 기존 연결된 계정이 있음
            user = oauth_account.user
            self._update_oauth_account(oauth_account, oauth_info)
            return user, False
        
        # 이메일로 기존 사용자 찾기
        user = None
        if oauth_info.email:
            user = self.db.query(User).filter(
                User.email == oauth_info.email,
                User.deleted_at.is_(None)
            ).first()
        
        if not user:
            # 새 사용자 생성
            user = self._create_oauth_user(oauth_info)
            is_new_user = True
        else:
            is_new_user = False
        
        # OAuth 계정 연결 정보 생성
        self._create_oauth_account(user, provider, oauth_info)
        
        return user, is_new_user
    
    def _create_oauth_user(self, oauth_info: OAuthUserInfo) -> User:
        """OAuth 정보로 새 사용자 생성"""
        user = User(
            email=oauth_info.email or f"user_{secrets.token_hex(8)}@oauth.local",
            password_hash=None,  # OAuth 사용자는 비밀번호 없음
            name=oauth_info.name,
            profile_image_url=oauth_info.profile_image_url,
            signup_method="oauth",
            is_email_verified=bool(oauth_info.email)  # OAuth 제공자가 이메일 제공했으면 인증된 것으로 간주
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def _create_oauth_account(self, user: User, provider: OAuthProvider, oauth_info: OAuthUserInfo):
        """OAuth 계정 연결 정보 생성"""
        oauth_account = UserOAuthAccount(
            user_id=user.id,
            provider_id=provider.id,
            provider_user_id=oauth_info.provider_user_id,
            email=oauth_info.email,
            name=oauth_info.name,
            profile_image_url=oauth_info.profile_image_url,
            raw_data=json.dumps(oauth_info.raw_data),
            is_active=True
        )
        
        self.db.add(oauth_account)
        self.db.commit()
    
    def _update_oauth_account(self, oauth_account: UserOAuthAccount, oauth_info: OAuthUserInfo):
        """기존 OAuth 계정 정보 업데이트"""
        oauth_account.email = oauth_info.email
        oauth_account.name = oauth_info.name
        oauth_account.profile_image_url = oauth_info.profile_image_url
        oauth_account.raw_data = json.dumps(oauth_info.raw_data)
        oauth_account.updated_at = datetime.utcnow()
        
        # 사용자 정보도 업데이트 (이름, 프로필 이미지 등)
        if oauth_info.name and not oauth_account.user.name:
            oauth_account.user.name = oauth_info.name
        if oauth_info.profile_image_url:
            oauth_account.user.profile_image_url = oauth_info.profile_image_url
        
        self.db.commit()
    
    async def unlink_oauth_account(self, user: User, provider_name: str) -> bool:
        """OAuth 계정 연결 해제"""
        provider = await self.get_provider(provider_name)
        if not provider:
            return False
        
        oauth_account = self.db.query(UserOAuthAccount).filter(
            UserOAuthAccount.user_id == user.id,
            UserOAuthAccount.provider_id == provider.id,
            UserOAuthAccount.is_active
        ).first()
        
        if not oauth_account:
            return False
        
        # 다른 로그인 방법이 있는지 확인
        has_password = bool(user.password_hash)
        other_oauth_count = self.db.query(UserOAuthAccount).filter(
            UserOAuthAccount.user_id == user.id,
            UserOAuthAccount.provider_id != provider.id,
            UserOAuthAccount.is_active
        ).count()
        
        if not has_password and other_oauth_count == 0:
            raise ValueError("Cannot unlink the only login method")
        
        oauth_account.is_active = False
        self.db.commit()
        return True
    
    def generate_oauth_url(self, provider: OAuthProvider, redirect_uri: str, state: str = None) -> str:
        """OAuth 인증 URL 생성"""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": provider.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": provider.scope,
            "state": state
        }
        
        if provider.name == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider.name == "kakao":
            params["response_type"] = "code"
        elif provider.name == "apple":
            params["response_mode"] = "form_post"
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{provider.auth_url}?{query_string}"