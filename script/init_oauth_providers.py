#!/usr/bin/env python3
"""
OAuth 제공자 초기 데이터 설정 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 파이썬 패스에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.oauth import OAuthProvider

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_oauth_providers():
    """OAuth 제공자 초기 데이터 생성"""
    db = SessionLocal()
    
    try:
        # 기존 데이터 확인
        existing_providers = db.query(OAuthProvider).all()
        if existing_providers:
            print("OAuth providers already exist. Skipping initialization.")
            return
        
        # OAuth 제공자들 정의
        providers = [
            {
                "name": "google",
                "display_name": "Google",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile"
            },
            {
                "name": "kakao",
                "display_name": "카카오톡",
                "auth_url": "https://kauth.kakao.com/oauth/authorize",
                "token_url": "https://kauth.kakao.com/oauth/token",
                "user_info_url": "https://kapi.kakao.com/v2/user/me",
                "scope": "profile_nickname profile_image account_email"
            },
            {
                "name": "apple",
                "display_name": "Apple",
                "auth_url": "https://appleid.apple.com/auth/authorize",
                "token_url": "https://appleid.apple.com/auth/token",
                "user_info_url": None,  # Apple은 ID token에 정보 포함
                "scope": "name email"
            }
        ]
        
        # 데이터베이스에 추가
        for provider_data in providers:
            provider = OAuthProvider(**provider_data)
            db.add(provider)
        
        db.commit()
        print("✅ OAuth providers initialized successfully!")
        
        # 생성된 제공자들 출력
        for provider in providers:
            print(f"   - {provider['display_name']} ({provider['name']})")
        
        print("\n📝 다음 단계:")
        print("   1. .env 파일에 각 제공자의 client_id와 client_secret 설정")
        print("   2. 각 OAuth 앱에서 redirect URI 설정")
        print("   3. 데이터베이스의 oauth_providers 테이블에서 클라이언트 정보 업데이트")
        
    except Exception as e:
        print(f"❌ Error initializing OAuth providers: {e}")
        db.rollback()
    finally:
        db.close()


def update_provider_credentials():
    """환경변수에서 OAuth 제공자 자격증명 업데이트"""
    db = SessionLocal()
    
    try:
        # Google
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if google_client_id:
            google_provider = db.query(OAuthProvider).filter(OAuthProvider.name == "google").first()
            if google_provider:
                google_provider.client_id = google_client_id
                google_provider.client_secret = google_client_secret
                print("✅ Google credentials updated")
        
        # 카카오
        kakao_client_id = os.getenv("KAKAO_CLIENT_ID")
        kakao_client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        
        if kakao_client_id:
            kakao_provider = db.query(OAuthProvider).filter(OAuthProvider.name == "kakao").first()
            if kakao_provider:
                kakao_provider.client_id = kakao_client_id
                kakao_provider.client_secret = kakao_client_secret
                print("✅ Kakao credentials updated")
        
        # Apple
        apple_client_id = os.getenv("APPLE_CLIENT_ID")
        apple_private_key = os.getenv("APPLE_PRIVATE_KEY")
        
        if apple_client_id:
            apple_provider = db.query(OAuthProvider).filter(OAuthProvider.name == "apple").first()
            if apple_provider:
                apple_provider.client_id = apple_client_id
                apple_provider.client_secret = apple_private_key  # Apple은 private key 사용
                print("✅ Apple credentials updated")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error updating credentials: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔐 Initializing OAuth providers...")
    init_oauth_providers()
    
    print("\n🔑 Updating credentials from environment variables...")
    update_provider_credentials()
    
    print("\n🎉 OAuth setup completed!")