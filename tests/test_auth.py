import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# 테스트용 인메모리 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_register(client):
    """회원가입 테스트"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "test@example.com"


def test_register_duplicate_email(client):
    """중복 이메일 회원가입 테스트"""
    # 첫 번째 사용자 등록
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # 같은 이메일로 다시 등록 시도
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "anotherpassword"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "already registered" in data["error"]


def test_login(client):
    """로그인 테스트"""
    # 먼저 사용자 등록
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # 로그인
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "access_token" in data["data"]


def test_login_invalid_credentials(client):
    """잘못된 로그인 정보 테스트"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] == False


def test_get_current_user(client):
    """현재 사용자 정보 조회 테스트"""
    # 사용자 등록 및 토큰 획득
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = register_response.json()["data"]["access_token"]
    
    # 토큰으로 사용자 정보 조회
    response = client.get(
        "/api/v1/members/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["email"] == "test@example.com"