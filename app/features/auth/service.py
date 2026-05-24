from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.features.accounts.models import Account
from app.features.accounts.service import get_account_by_email


async def authenticate_account(db: AsyncSession, username: str, password: str) -> Account | None:
    account = await get_account_by_email(db, username)
    if account is None or not verify_password(password, account.password_hash):
        return None

    return account
