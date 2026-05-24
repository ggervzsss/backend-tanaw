from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.accounts.models import Account
from app.features.accounts.schemas import AuthUser


def to_auth_user(account: Account) -> AuthUser:
    return AuthUser(
        id=account.id,
        email=account.email,
        displayName=account.display_name,
        role=account.role.value,
        title=account.title,
    )


async def get_account_by_email(db: AsyncSession, email: str) -> Account | None:
    return await db.scalar(select(Account).where(Account.email == email.lower()))


async def get_account_by_id(db: AsyncSession, account_id: str) -> Account | None:
    return await db.scalar(select(Account).where(Account.id == account_id))


async def record_login(db: AsyncSession, account: Account) -> None:
    account.last_login_at = datetime.now(UTC)
    await db.commit()
