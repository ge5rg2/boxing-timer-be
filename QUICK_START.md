# 🚀 빠른 시작 가이드

이 가이드를 따라하면 5분 안에 복싱 타이머 API를 실행할 수 있습니다.

## 📋 사전 요구사항

- Python 3.12+
- Docker & Docker Compose (선택사항)
- PostgreSQL (또는 Docker 사용)

## 🔧 1단계: 프로젝트 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd boxing-timer-api

# 환경변수 설정
cp .env.example .env
```

`.env` 파일을 열어서 다음 항목들을 수정하세요:

```bash
# 필수 수정 항목
SECRET_KEY=your-super-secret-key-here-minimum-32-characters
DATABASE_URL=postgresql://postgres:password@localhost:5432/boxing_timer

# 선택사항
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

## 📦 2단계: 의존성 설치

```bash
# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 🗄️ 3단계: 데이터베이스 설정

### 옵션 A: Docker 사용 (추천)

```bash
# 데이터베이스만 Docker로 실행
docker-compose up -d db

# 5초 정도 기다린 후 마이그레이션 실행
sleep 5
alembic upgrade head
```

### 옵션 B: 로컬 PostgreSQL 사용

```bash
# PostgreSQL에 데이터베이스 생성
createdb boxing_timer

# 마이그레이션 실행
alembic upgrade head
```

## 🚀 4단계: 서버 실행

```bash
# 개발 서버 실행
python scripts/run_dev.py

# 또는 직접 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ 5단계: 동작 확인

브라우저에서 다음 주소들을 확인해보세요:

- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health
- **메인 페이지**: http://localhost:8000

## 🧪 6단계: API 테스트

### 1. 회원가입

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 2. 사이클 생성

```bash
# 위에서 받은 토큰을 사용
curl -X POST "http://localhost:8000/api/v1/cycles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "기본 복싱 트레이닝",
    "description": "3라운드 기본 트레이닝",
    "total_rounds": 3,
    "cycle_rest_seconds": 60
  }'
```

## 🐳 Docker로 전체 실행

모든 것을 Docker로 실행하려면:

```bash
# 전체 스택 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f api
```

## 🛠 유용한 명령어들

```bash
# Makefile 사용 (더 간단함)
make setup      # 초기 설정
make install    # 의존성 설치
make dev        # 개발 서버 실행
make test       # 테스트 실행
make migration  # 새 마이그레이션 생성
make migrate    # 마이그레이션 적용

# 직접 명령어
alembic revision --autogenerate -m "메시지"  # 새 마이그레이션
alembic upgrade head                        # 마이그레이션 적용
pytest tests/                              # 테스트 실행
```

## 🔍 문제 해결

### 데이터베이스 연결 오류

```bash
# PostgreSQL 서비스 확인
docker-compose ps
docker-compose logs db

# 포트 확인
netstat -an | grep 5432
```

### 패키지 설치 오류

```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000
kill -9 PID  # 필요시 프로세스 종료
```

## 📚 다음 단계

1. **API 문서 탐색**: http://localhost:8000/docs에서 모든 엔드포인트 확인
2. **테스트 작성**: `tests/` 디렉토리에 추가 테스트 작성
3. **프론트엔드 연동**: Flutter 앱과 API 연결
4. **배포 준비**: AWS, Docker 등을 활용한 배포

## 🆘 도움이 필요한가요?

- **API 문서**: http://localhost:8000/docs
- **이슈 리포트**: GitHub Issues
- **이메일**: [개발자 이메일]

---

**Happy Coding! 🥊**
