"""
API v1 Package

API 버전 1의 모든 라우터들을 통합 관리
"""

from fastapi import APIRouter
from . import auth, members, cycles, rounds, combinations, workouts, oauth, migration

# v1 통합 라우터 생성
router = APIRouter()

# 개별 라우터들을 통합 라우터에 포함
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
router.include_router(migration.router, prefix="/migration", tags=["Migration"])
router.include_router(members.router, prefix="/members", tags=["Members"]) 
router.include_router(cycles.router, prefix="/cycles", tags=["Cycles"])
router.include_router(rounds.router, prefix="/cycles/{cycle_id}/rounds", tags=["Rounds"])
router.include_router(combinations.router, prefix="/combinations", tags=["Combinations"])
router.include_router(workouts.router, prefix="/workouts", tags=["Workouts"])

__all__ = ["router", "auth", "oauth", "migration", "members", "cycles", "rounds", "combinations", "workouts"]