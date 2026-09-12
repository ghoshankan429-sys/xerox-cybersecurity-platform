from datetime import datetime, timezone
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.security.tokens import hash_session_token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency validating the HttpOnly session cookie against database records.
    Returns the authenticated User or raises HTTP 401.
    """
    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_hash = hash_session_token(session_token)
    now = datetime.now(timezone.utc)

    # Query active session
    stmt = (
        select(UserSession)
        .where(
            UserSession.session_token_hash == token_hash,
            UserSession.expires_at > now,
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    # Query user associated with session
    user_stmt = select(User).where(User.id == session.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with session does not exist",
        )

    return user
