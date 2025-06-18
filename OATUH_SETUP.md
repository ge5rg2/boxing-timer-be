# 🔐 OAuth 설정 가이드

복싱 타이머 앱에서 소셜 로그인(Google, 카카오, Apple)을 설정하는 방법입니다.

## 📋 지원하는 OAuth 제공자

- **Google** - 안드로이드, iOS, 웹
- **카카오톡** - 안드로이드, iOS, 웹
- **Apple** - iOS, 웹 (Sign in with Apple)

## 🛠 1단계: OAuth 앱 등록

### Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 사용자 인증 정보** 이동
4. **사용자 인증 정보 만들기 > OAuth 2.0 클라이언트 ID** 선택
5. 애플리케이션 유형:
   - **웹 애플리케이션** (웹용)
   - **Android** (안드로이드용)
   - **iOS** (iOS용)

```bash
# 승인된 리디렉션 URI 예시
http://localhost:8000/api/v1/oauth/google/callback
https://yourdomain.com/api/v1/oauth/google/callback

# 모바일 앱의 경우
com.yourapp.boxingtimer://oauth/google/callback
```

### 카카오 OAuth 설정

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. **내 애플리케이션 > 애플리케이션 추가하기**
3. **제품 설정 > 카카오 로그인** 활성화
4. **Redirect URI** 설정:

```bash
# 웹용
http://localhost:8000/api/v1/oauth/kakao/callback
https://yourdomain.com/api/v1/oauth/kakao/callback

# 모바일용
com.yourapp.boxingtimer://oauth/kakao/callback
```

5. **동의항목** 설정:
   - 프로필 정보(닉네임/프로필 사진): 선택 동의
   - 카카오계정(이메일):
