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

    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    if not user.is_active:
        raise AccountDisabledError()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)
