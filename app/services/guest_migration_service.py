import json
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import (
    User, UserCycle, UserCombination, WorkoutLog, MigrationLog
)


class GuestDataMigrationService:
    """비회원 데이터를 회원 계정으로 이전하는 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def preview_migration_data(self, session_id: str) -> Dict:
        """
        마이그레이션될 데이터 미리보기
        
        Args:
            session_id: 비회원 세션 ID
            
        Returns:
            마이그레이션 가능한 데이터 정보
        """
        try:
            # 사이클 개수 확인
            cycles_count = self.db.query(UserCycle).filter(
                UserCycle.user_id.is_(None),
                UserCycle.session_id == session_id,
                UserCycle.deleted_at.is_(None)
            ).count()
            
            # 컴비네이션 개수 확인
            combinations_count = self.db.query(UserCombination).filter(
                UserCombination.user_id.is_(None),
                UserCombination.session_id == session_id,
                UserCombination.deleted_at.is_(None)
            ).count()
            
            # 운동 기록 개수 확인
            workout_logs_count = self.db.query(WorkoutLog).filter(
                WorkoutLog.user_id.is_(None),
                WorkoutLog.session_id == session_id
            ).count()
            
            # 상세 정보 조회 (미리보기용)
            cycle_titles = [
                cycle.title for cycle in self.db.query(UserCycle.title).filter(
                    UserCycle.user_id.is_(None),
                    UserCycle.session_id == session_id,
                    UserCycle.deleted_at.is_(None)
                ).limit(5).all()
            ]
            
            combination_titles = [
                combo.title for combo in self.db.query(UserCombination.title).filter(
                    UserCombination.user_id.is_(None),
                    UserCombination.session_id == session_id,
                    UserCombination.deleted_at.is_(None)
                ).limit(5).all()
            ]
            
            return {
                "cycles_count": cycles_count,
                "combinations_count": combinations_count,
                "workout_logs_count": workout_logs_count,
                "has_data": cycles_count > 0 or combinations_count > 0 or workout_logs_count > 0,
                "preview": {
                    "cycle_titles": cycle_titles,
                    "combination_titles": combination_titles
                }
            }
            
        except Exception as e:
            return {
                "cycles_count": 0,
                "combinations_count": 0,
                "workout_logs_count": 0,
                "has_data": False,
                "error": str(e)
            }
    
    def migrate_guest_data_to_user(self, session_id: str, user: User) -> Dict:
        """
        비회원 데이터를 회원 계정으로 이전
        
        Args:
            session_id: 비회원 세션 ID
            user: 이전받을 회원 계정
            
        Returns:
            마이그레이션 결과 정보
        """
        migration_started_at = datetime.utcnow()
        
        # 마이그레이션 로그 생성
        migration_log = MigrationLog(
            session_id=session_id,
            user_id=user.id,
            migration_status="in_progress",
            migration_started_at=migration_started_at
        )
        self.db.add(migration_log)
        self.db.flush()  # ID 생성을 위해 flush
        
        result = {
            "cycles_migrated": 0,
            "combinations_migrated": 0,
            "workout_logs_migrated": 0,
            "errors": [],
            "migration_log_id": migration_log.id
        }
        
        try:
            # 이미 마이그레이션된 세션인지 확인
            existing_migration = self.db.query(MigrationLog).filter(
                MigrationLog.session_id == session_id,
                MigrationLog.migration_status == "success"
            ).first()
            
            if existing_migration:
                raise ValueError(f"Session {session_id} already migrated to user {existing_migration.user_id}")
            
            # 1. 사이클 데이터 이전
            result["cycles_migrated"] = self._migrate_cycles(session_id, user, result["errors"])
            
            # 2. 컴비네이션 데이터 이전
            result["combinations_migrated"] = self._migrate_combinations(session_id, user, result["errors"])
            
            # 3. 운동 기록 이전
            result["workout_logs_migrated"] = self._migrate_workout_logs(session_id, user, result["errors"])
            
            # 4. 마이그레이션 완료 처리
            migration_log.cycles_migrated = result["cycles_migrated"]
            migration_log.combinations_migrated = result["combinations_migrated"]
            migration_log.workout_logs_migrated = result["workout_logs_migrated"]
            migration_log.migration_completed_at = datetime.utcnow()
            
            if result["errors"]:
                migration_log.migration_status = "partial"
                migration_log.error_details = json.dumps(result["errors"], ensure_ascii=False)
            else:
                migration_log.migration_status = "success"
            
            # 모든 변경사항 커밋
            self.db.commit()
            
        except Exception as e:
            # 오류 발생 시 롤백
            self.db.rollback()
            
            # 마이그레이션 로그 업데이트
            migration_log.migration_status = "failed"
            migration_log.error_details = str(e)
            migration_log.migration_completed_at = datetime.utcnow()
            
            try:
                self.db.commit()
            except:
                pass  # 로그 저장 실패해도 무시
            
            result["errors"].append(str(e))
            raise
        
        return result
    
    def _migrate_cycles(self, session_id: str, user: User, errors: List[str]) -> int:
        """사이클 데이터 마이그레이션"""
        migrated_count = 0
        
        guest_cycles = self.db.query(UserCycle).filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id,
            UserCycle.deleted_at.is_(None)
        ).all()
        
        for cycle in guest_cycles:
            try:
                # 중복 제목 확인 및 처리
                original_title = cycle.title
                new_title = self._get_unique_cycle_title(user.id, cycle.title)
                
                if new_title != original_title:
                    cycle.title = new_title
                
                # 사용자 ID 설정 및 세션 ID 제거
                cycle.user_id = user.id
                cycle.session_id = None
                
                migrated_count += 1
                
                # 제목이 변경된 경우 로그에 기록
                if new_title != original_title:
                    errors.append(f"사이클 '{original_title}' → '{new_title}'로 이름 변경됨")
                
            except Exception as e:
                errors.append(f"사이클 '{cycle.title}' 마이그레이션 실패: {str(e)}")
                continue
        
        return migrated_count
    
    def _migrate_combinations(self, session_id: str, user: User, errors: List[str]) -> int:
        """컴비네이션 데이터 마이그레이션"""
        migrated_count = 0
        
        guest_combinations = self.db.query(UserCombination).filter(
            UserCombination.user_id.is_(None),
            UserCombination.session_id == session_id,
            UserCombination.deleted_at.is_(None)
        ).all()
        
        for combination in guest_combinations:
            try:
                # 중복 제목 확인 및 처리
                original_title = combination.title
                new_title = self._get_unique_combination_title(user.id, combination.title)
                
                if new_title != original_title:
                    combination.title = new_title
                
                # 사용자 ID 설정 및 세션 ID 제거
                combination.user_id = user.id
                combination.session_id = None
                
                migrated_count += 1
                
                # 제목이 변경된 경우 로그에 기록
                if new_title != original_title:
                    errors.append(f"컴비네이션 '{original_title}' → '{new_title}'로 이름 변경됨")
                
            except Exception as e:
                errors.append(f"컴비네이션 '{combination.title}' 마이그레이션 실패: {str(e)}")
                continue
        
        return migrated_count
    
    def _migrate_workout_logs(self, session_id: str, user: User, errors: List[str]) -> int:
        """운동 기록 마이그레이션"""
        migrated_count = 0
        
        guest_workout_logs = self.db.query(WorkoutLog).filter(
            WorkoutLog.user_id.is_(None),
            WorkoutLog.session_id == session_id
        ).all()
        
        for workout_log in guest_workout_logs:
            try:
                # 사용자 ID 설정 및 세션 ID 제거
                workout_log.user_id = user.id
                workout_log.session_id = None
                
                migrated_count += 1
                
            except Exception as e:
                errors.append(f"운동 기록 {workout_log.id} 마이그레이션 실패: {str(e)}")
                continue
        
        return migrated_count
    
    def _get_unique_cycle_title(self, user_id: int, title: str) -> str:
        """중복되지 않는 사이클 제목 생성"""
        original_title = title
        counter = 1
        
        while True:
            existing_cycle = self.db.query(UserCycle).filter(
                UserCycle.user_id == user_id,
                UserCycle.title == title,
                UserCycle.deleted_at.is_(None)
            ).first()
            
            if not existing_cycle:
                return title
            
            # 중복되면 번호 추가
            title = f"{original_title} ({counter})"
            counter += 1
            
            # 무한 루프 방지 (최대 100회)
            if counter > 100:
                title = f"{original_title} (마이그레이션-{datetime.now().strftime('%m%d%H%M')})"
                break
        
        return title
    
    def _get_unique_combination_title(self, user_id: int, title: str) -> str:
        """중복되지 않는 컴비네이션 제목 생성"""
        original_title = title
        counter = 1
        
        while True:
            existing_combination = self.db.query(UserCombination).filter(
                UserCombination.user_id == user_id,
                UserCombination.title == title,
                UserCombination.deleted_at.is_(None)
            ).first()
            
            if not existing_combination:
                return title
            
            # 중복되면 번호 추가
            title = f"{original_title} ({counter})"
            counter += 1
            
            # 무한 루프 방지 (최대 100회)
            if counter > 100:
                title = f"{original_title} (마이그레이션-{datetime.now().strftime('%m%d%H%M')})"
                break
        
        return title
    
    def get_migration_history(self, user_id: int) -> List[Dict]:
        """사용자의 마이그레이션 이력 조회"""
        migrations = self.db.query(MigrationLog).filter(
            MigrationLog.user_id == user_id
        ).order_by(MigrationLog.created_at.desc()).all()
        
        return [
            {
                "id": migration.id,
                "session_id": migration.session_id,
                "cycles_migrated": migration.cycles_migrated,
                "combinations_migrated": migration.combinations_migrated,
                "workout_logs_migrated": migration.workout_logs_migrated,
                "status": migration.migration_status,
                "started_at": migration.migration_started_at,
                "completed_at": migration.migration_completed_at,
                "errors": json.loads(migration.error_details) if migration.error_details else []
            }
            for migration in migrations
        ]
    
    def cleanup_old_guest_data(self, days_old: int = 30) -> Dict:
        """오래된 비회원 데이터 정리"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # 오래된 비회원 데이터 조회
        old_cycles = self.db.query(UserCycle).filter(
            UserCycle.user_id.is_(None),
            UserCycle.created_at < cutoff_date
        )
        
        old_combinations = self.db.query(UserCombination).filter(
            UserCombination.user_id.is_(None),
            UserCombination.created_at < cutoff_date
        )
        
        old_workout_logs = self.db.query(WorkoutLog).filter(
            WorkoutLog.user_id.is_(None),
            WorkoutLog.created_at < cutoff_date
        )
        
        # 개수 세기
        cycles_count = old_cycles.count()
        combinations_count = old_combinations.count()
        workout_logs_count = old_workout_logs.count()
        
        # 삭제 실행
        old_cycles.delete(synchronize_session=False)
        old_combinations.delete(synchronize_session=False)
        old_workout_logs.delete(synchronize_session=False)
        
        self.db.commit()
        
        return {
            "cycles_deleted": cycles_count,
            "combinations_deleted": combinations_count,
            "workout_logs_deleted": workout_logs_count,
            "cutoff_date": cutoff_date
        }