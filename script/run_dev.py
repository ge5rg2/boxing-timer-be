#!/usr/bin/env python3
"""
개발환경 실행 스크립트
"""
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent

def check_env_file():
    """환경변수 파일 확인"""
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        print("❌ .env 파일이 없습니다.")
        print("📝 .env.example 파일을 복사해서 .env 파일을 만들어주세요.")
        print(f"   cp {ROOT_DIR}/.env.example {ROOT_DIR}/.env")
        return False
    return True

def check_dependencies():
    """의존성 패키지 확인"""
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        print("✅ 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 설치되지 않았습니다: {e}")
        print("📦 다음 명령어로 설치해주세요:")
        print(f"   pip install -r {ROOT_DIR}/requirements.txt")
        return False

def start_database():
    """데이터베이스 컨테이너 시작"""
    print("🗄️  데이터베이스 컨테이너를 시작합니다...")
    try:
        subprocess.run([
            "docker", "compose", "up", "-d", "db"
        ], cwd=ROOT_DIR, check=True)
        print("✅ 데이터베이스가 시작되었습니다.")
        return True
    except subprocess.CalledProcessError:
        print("❌ 데이터베이스 시작에 실패했습니다.")
        print("🐳 Docker가 설치되어 있고 실행 중인지 확인해주세요.")
        return False

def run_migrations():
    """데이터베이스 마이그레이션 실행"""
    print("🔄 데이터베이스 마이그레이션을 실행합니다...")
    try:
        # Alembic 초기화 (처음 실행시)
        subprocess.run([
            "alembic", "revision", "--autogenerate", "-m", "Initial migration"
        ], cwd=ROOT_DIR, check=False)
        
        # 마이그레이션 실행
        subprocess.run([
            "alembic", "upgrade", "head"
        ], cwd=ROOT_DIR, check=True)
        print("✅ 마이그레이션이 완료되었습니다.")
        return True
    except subprocess.CalledProcessError:
        print("❌ 마이그레이션 실행에 실패했습니다.")
        return False

def start_api():
    """API 서버 시작"""
    print("🚀 API 서버를 시작합니다...")
    print("📍 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🛑 서버 종료: Ctrl+C")
    
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=ROOT_DIR)
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")

def main():
    """메인 실행 함수"""
    print("🥊 Boxing Timer API 개발 서버 시작")
    print("=" * 50)
    
    # 환경 확인
    if not check_env_file():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # 데이터베이스 시작
    if not start_database():
        print("⚠️  데이터베이스 없이 진행합니다. (SQLite 사용)")
    
    # 마이그레이션 실행
    run_migrations()
    
    # API 서버 시작
    start_api()

if __name__ == "__main__":
    main()