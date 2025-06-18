"""
API Response Schemas

Pydantic 모델들을 정의하여 API 요청/응답 검증 및 직렬화 담당
"""

# User schemas
from .user import (
    UserRegister, UserLogin, PasswordChange, UserUpdate,
    UserResponse, TokenResponse, SubscriptionResponse
)

# Cycle schemas  
from .cycle import (
    CycleCreate, CycleUpdate, CycleResponse, CycleListResponse,
    RoundCreate, RoundUpdate, RoundResponse,
    RoundCombinationCreate, RoundCombinationUpdate, RoundCombinationResponse,
    CycleTemplateResponse
)

# Combination schemas
from .combination import (
    CombinationCreate, CombinationUpdate, CombinationResponse,
    CombinationTemplateResponse
)

# Workout schemas
from .workout import (
    WorkoutStart, WorkoutComplete, WorkoutPause,
    WorkoutLogResponse, WorkoutHistoryResponse, WorkoutRoundLogResponse
)

# OAuth 스키마들 추가
from .oauth import (
    GoogleLoginRequest, KakaoLoginRequest, AppleLoginRequest,
    OAuthAccountResponse, OAuthProviderResponse, OAuthUnlinkRequest,
    OAuthURLRequest, OAuthURLResponse
)

# migration schemas
from .migration import (
    MigrationPreviewRequest, MigrationPreviewResponse, MigrationExecuteRequest,
    MigrationResultResponse, MigrationHistoryResponse, MigrationLogDetailResponse,
    CleanupResultResponse, MigrationStatsResponse
)
# Common response schemas
from .response import (
    ApiResponse, PaginatedResponse, PaginationMeta, ErrorResponse
)
__all__ = [
    # User
    "UserRegister", "UserLogin", "PasswordChange", "UserUpdate",
    "UserResponse", "TokenResponse", "SubscriptionResponse",
    
    # Cycle
    "CycleCreate", "CycleUpdate", "CycleResponse", "CycleListResponse",
    "RoundCreate", "RoundUpdate", "RoundResponse", 
    "RoundCombinationCreate", "RoundCombinationUpdate", "RoundCombinationResponse",
    "CycleTemplateResponse",
    
    # Combination
    "CombinationCreate", "CombinationUpdate", "CombinationResponse",
    "CombinationTemplateResponse",
    
    # Workout
    "WorkoutStart", "WorkoutComplete", "WorkoutPause",
    "WorkoutLogResponse", "WorkoutHistoryResponse", "WorkoutRoundLogResponse",

    # OAuth 추가
    "GoogleLoginRequest", "KakaoLoginRequest", "AppleLoginRequest",
    "OAuthAccountResponse", "OAuthProviderResponse", "OAuthUnlinkRequest", 
    "OAuthURLRequest", "OAuthURLResponse",

    # Migration
    "MigrationPreviewRequest", "MigrationPreviewResponse", "MigrationExecuteRequest",
    "MigrationResultResponse", "MigrationHistoryResponse", "MigrationLogDetailResponse",
    "CleanupResultResponse", "MigrationStatsResponse"
    
    # Response
    "ApiResponse", "PaginatedResponse", "PaginationMeta", "ErrorResponse"
]