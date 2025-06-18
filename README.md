# 🥊 Boxing Timer API

복싱 트레이닝을 위한 커스터마이징 타이머 앱의 백엔드 API입니다.

## 📋 기능

- **사용자 인증**: JWT 기반 로그인/회원가입
- **사이클 관리**: 커스텀 트레이닝 사이클 생성 및 관리
- **라운드 구성**: 각 사이클 내 라운드별 시간 설정
- **컴비네이션**: 라운드 내 동작 조합 및 음성 안내
- **운동 로그**: 트레이닝 세션 기록 및 통계
- **비회원 지원**: 로그인 없이도 기본 기능 사용 가능

## 🛠 기술 스택

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT
- **Validation**: Pydantic
- **Migration**: Alembic
- **Container**: Docker & Docker Compose

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone <repository-url>
cd boxing-timer-api
```

### 2. 환경 설정

```bash
# 환경변수 파일 생성
cp .env.example .env

# .env 파일에서 필요한 설정 수정
# - DATABASE_URL
# - SECRET_KEY
# - 기타 설정들
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 개발 서버 실행

```bash
# 간단한 방법 (추천)
python scripts/run_dev.py

# 또는 직접 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Docker로 실행

```bash
# 전체 스택 실행
docker-compose up -d

# 개발용 (API만 로컬에서 실행)
docker-compose up -d db redis
python scripts/run_dev.py
```

## 📚 API 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂 프로젝트 구조

```
boxing-timer-api/
├── app/
│   ├── api/v1/           # API 라우터
│   ├── core/             # 핵심 로직 (인증, 보안)
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── services/         # 비즈니스 로직
│   ├── config.py         # 설정 관리
│   ├── database.py       # DB 연결
│   ├── dependencies.py   # 의존성 주입
│   └── main.py          # FastAPI 앱
├── alembic/             # DB 마이그레이션
├── scripts/             # 유틸리티 스크립트
├── tests/               # 테스트 코드
├── docker-compose.yml   # Docker 설정
├── Dockerfile          # 컨테이너 이미지
├── requirements.txt    # Python 의존성
└── README.md
```

## 🔧 주요 API 엔드포인트

### 인증 (`/api/v1/auth`)

- `POST /register` - 회원가입
- `POST /login` - 로그인
- `POST /change-password` - 비밀번호 변경
- `POST /logout` - 로그아웃

### 사용자 (`/api/v1/members`)

- `GET /me` - 내 정보 조회
- `PATCH /{memberId}` - 사용자 정보 수정

### 사이클 (`/api/v1/cycles`)

- `GET /` - 사이클 목록 조회
- `POST /` - 새 사이클 생성
- `GET /{cycleId}` - 사이클 상세 조회
- `PATCH /{cycleId}` - 사이클 수정
- `DELETE /{cycleId}` - 사이클 삭제

### 라운드 (`/api/v1/cycles/{cycleId}/rounds`)

- `GET /` - 라운드 목록 조회
- `POST /` - 라운드 추가
- `PATCH /{roundId}` - 라운드 수정
- `DELETE /{roundId}` - 라운드 삭제

### 컴비네이션 (`/api/v1/combinations`)

- `GET /` - 컴비네이션 목록 조회
- `POST /` - 컴비네이션 생성
- `PATCH /{combinationId}` - 컴비네이션 수정
- `DELETE /{combinationId}` - 컴비네이션 삭제

### 운동 기록 (`/api/v1/workouts`)

- `POST /start` - 운동 세션 시작
- `PATCH /{sessionId}/complete` - 운동 완료
- `PATCH /{sessionId}/pause` - 일시정지
- `GET /history` - 운동 기록 조회

## 🔐 인증 방식

JWT Bearer Token을 사용합니다:

```bash
# 헤더에 토큰 포함
Authorization: Bearer <your-jwt-token>
```

## 🧪 테스트

```bash
# 단위 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app

# 특정 테스트 파일만
pytest tests/test_auth.py
```

## 🗄 데이터베이스 마이그레이션

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 🌍 배포

### Docker를 이용한 배포

```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up -d

# 또는 개별 빌드
docker build -t boxing-timer-api .
docker run -p 8000:8000 boxing-timer-api
```

### AWS 배포 (예시)

```bash
# ECR에 이미지 푸시
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag boxing-timer-api:latest <account>.dkr.ecr.ap-northeast-2.amazonaws.com/boxing-timer-api:latest
docker push <account>.dkr.ecr.ap-northeast-2.amazonaws.com/boxing-timer-api:latest
```

## 📝 환경변수

주요 환경변수는 `.env.example` 파일을 참고하세요:

- `DATABASE_URL`: PostgreSQL 연결 URL
- `SECRET_KEY`: JWT 토큰 서명 키
- `DEBUG`: 디버그 모드 활성화
- `ALLOWED_ORIGINS`: CORS 허용 도메인

## 🤝 기여

1. 이 저장소를 포크합니다
2. 새 기능 브랜치를 만듭니다 (`git checkout -b feature/new-feature`)
3. 변경사항을 커밋합니다 (`git commit -am 'Add new feature'`)
4. 브랜치를 푸시합니다 (`git push origin feature/new-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- 개발자: [George Kim]
- 이메일: [roypapakim51@gmail.com]
- 이슈: [GitHub Issues](링크)

---

**Happy Boxing! 🥊**
