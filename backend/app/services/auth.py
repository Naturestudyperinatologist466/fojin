from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.exceptions import (
    AccountDisabledError,
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
)
from app.models.user import User
from app.schemas.user import TokenResponse, UserRegister


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    # Check username
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise DuplicateUsernameError()

    # Check email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise DuplicateEmailError()

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        display_name=data.display_name or data.username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    # Always run password verification to prevent timing-based user enumeration.
    # When user is not found, verify against a dummy hash so the response time
    # is indistinguishable from an incorrect-password attempt.
    _dummy_hash = "$2b$12$LJ3m4ys3Lz0Y1vVTqHKZaeflVbOBGSJl6Nnb3CiZ3sCImt9Ghmiy"
    if not verify_password(password, user.hashed_password if user else _dummy_hash) or user is None:
        raise InvalidCredentialsError()

    if not user.is_active:
        raise AccountDisabledError()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)
