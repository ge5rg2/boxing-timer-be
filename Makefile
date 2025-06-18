# Boxing Timer API Makefile

# 변수 정의
PYTHON = python3
PIP = pip3
APP_NAME = boxing-timer-api
DOCKER_IMAGE = $(APP_NAME):latest

# 기본 타겟
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  setup       - 초기 환경 설정"
	@echo "  install     - 의존성 패키지 설치"
	@echo "  dev         - 개발 서버 실행"
	@echo "  test        - 테스트 실행"
	@echo "  lint        - 코드 린팅"
	@echo "  format      - 코드 포맷팅"
	@echo "  migration   - 새 마이그레이션 생성"
	@echo "  migrate     - 마이그레이션 적용"
	@echo "  docker-build - Docker 이미지 빌드"
	@echo "  docker-run  - Docker 컨테이너 실행"
	@echo "  clean       - 캐시 및 임시 파일 정리"

# 초기 환경 설정
.PHONY: setup
setup:
	@echo "🔧 초기 환경을 설정합니다..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "✅ .env 파일이 생성되었습니다. 필요한 설정을 수정해주세요."

# 의존성 설치
.PHONY: install
install:
	@echo "📦 의존성 패키지를 설치합니다..."
	$(PIP) install -r requirements.txt
	@echo "✅ 설치 완료!"

# 개발 서버 실행
.PHONY: dev
dev:
	@echo "🚀 개발 서버를 시작합니다..."
	$(PYTHON) scripts/run_dev.py

# 테스트 실행
.PHONY: test
test:
	@echo "🧪 테스트를 실행합니다..."
	pytest tests/ -v

# 테스트 (커버리지 포함)
.PHONY: test-cov
test-cov:
	@echo "🧪 테스트를 실행합니다 (커버리지 포함)..."
	pytest tests/ -v --cov=app --cov-report=html

# 코드 린팅
.PHONY: lint
lint:
	@echo "🔍 코드 린팅을 실행합니다..."
	flake8 app tests
	@echo "✅ 린팅 완료!"

# 코드 포맷팅
.PHONY: format
format:
	@echo "🎨 코드 포맷팅을 실행합니다..."
	black app tests
	isort app tests
	@echo "✅ 포맷팅 완료!"

# 새 마이그레이션 생성
.PHONY: migration
migration:
	@echo "📝 새 마이그레이션을 생성합니다..."
	@read -p "마이그레이션 메시지를 입력하세요: " message; \
	alembic revision --autogenerate -m "$$message"

# 마이그레이션 적용
.PHONY: migrate
migrate:
	@echo "🔄 마이그레이션을 적용합니다..."
	alembic upgrade head
	@echo "✅ 마이그레이션 완료!"

# 마이그레이션 롤백
.PHONY: downgrade
downgrade:
	@echo "⏪ 마이그레이션을 롤백합니다..."
	alembic downgrade -1

# Docker 이미지 빌드
.PHONY: docker-build
docker-build:
	@echo "🐳 Docker 이미지를 빌드합니다..."
	docker build -t $(DOCKER_IMAGE) .
	@echo "✅ 빌드 완료!"

# Docker 컨테이너 실행
.PHONY: docker-run
docker-run:
	@echo "🐳 Docker 컨테이너를 실행합니다..."
	docker-compose up -d
	@echo "✅ 컨테이너 실행 완료!"

# Docker 컨테이너 중지
.PHONY: docker-stop
docker-stop:
	@echo "🛑 Docker 컨테이너를 중지합니다..."
	docker-compose down
	@echo "✅ 컨테이너 중지 완료!"

# 데이터베이스만 실행
.PHONY: db-start
db-start:
	@echo "🗄️ 데이터베이스를 시작합니다..."
	docker-compose up -d db
	@echo "✅ 데이터베이스 시작 완료!"

# 캐시 및 임시 파일 정리
.PHONY: clean
clean:
	@echo "🧹 캐시 및 임시 파일을 정리합니다..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ 정리 완료!"

# 전체 설정 (처음 실행)
.PHONY: init
init: setup install migration migrate
	@echo "🎉 초기 설정이 완료되었습니다!"
	@echo "이제 'make dev' 명령어로 개발 서버를 시작할 수 있습니다."