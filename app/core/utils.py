from typing import Optional
from sqlalchemy.orm import Query
from app.models import User, UserCycle, UserCombination


def filter_user_cycle_by_auth(
    query: Query,
    user: Optional[User],
    session_id: str
) -> Query:
    """
    유저 or 세션 기반 필터링이 적용된 UserCycle 쿼리 객체를 반환
    """
    query = query.filter(UserCycle.deleted_at.is_(None))
    
    if user:
        query = query.filter(UserCycle.user_id == user.id)
    else:
        query = query.filter(
            UserCycle.user_id.is_(None),
            UserCycle.session_id == session_id
        )
    
    return query

def filter_user_combination_by_auth(
    query: Query,
    user: Optional[User],
    session_id: str
) -> Query: 
    """
    유저 & 세션 기반 필터링 적용된 Usercombination 쿼리 객체를 반환
    """
    query = query.filter(UserCombination.deleted_at.is_(None))
    
    if user:
        query= query.filter(UserCombination.user_id == user.id)
    else:
        query= query.filter(
            UserCombination.user_id.is_(None),
            UserCombination.session_id == session_id
        )

    return query
