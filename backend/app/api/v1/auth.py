from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest, UserResponse
from app.security.dependencies import get_current_user
from app.security.passwords import hash_password, verify_password
from app.security.rate_limiter import login_rate_limiter
from app.security.tokens import generate_session_token, hash_session_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_client_ip(request: Request) -> str:
    """Extracts client IP address safely from request headers or socket."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new analyst account",
)
async def register_user(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    # Check for duplicate email
    stmt = select(User).where(User.email == req.email)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password securely
    hashed = hash_password(req.password)

    new_user = User(
        email=req.email,
        password_hash=hashed,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Authenticate and establish an HttpOnly cookie session",
)
async def login_user(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    client_ip = _get_client_ip(request)
    rate_limit_key = f"{client_ip}:{req.email}"

    # Verify brute-force threshold
    login_rate_limiter.check_rate_limit(rate_limit_key)

    # Query user account
    stmt = select(User).where(User.email == req.email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    # Generic credential check preventing email enumeration
    if not user or not verify_password(req.password, user.password_hash):
        login_rate_limiter.record_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Reset failure counter on success
    login_rate_limiter.record_success(rate_limit_key)

    # Generate session token and store hash in database
    session_token = generate_session_token()
    token_hash = hash_session_token(session_token)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)

    new_session = UserSession(
        user_id=user.id,
        session_token_hash=token_hash,
        expires_at=expires_at,
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent", "")[:512],
    )
    db.add(new_session)
    await db.commit()

    # Set secure HttpOnly session cookie
    is_secure = settings.COOKIE_SECURE or (settings.ENVIRONMENT == "production")
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        max_age=settings.SESSION_EXPIRE_SECONDS,
        httponly=True,
        secure=is_secure,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )

    return user


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Invalidate current session and clear HttpOnly cookie",
)
async def logout_user(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if session_token:
        token_hash = hash_session_token(session_token)
        await db.execute(
            delete(UserSession).where(UserSession.session_token_hash == token_hash)
        )
        await db.commit()

    # Invalidate cookie on browser
    is_secure = settings.COOKIE_SECURE or (settings.ENVIRONMENT == "production")
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        secure=is_secure,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )

    return MessageResponse(message="Successfully logged out.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
