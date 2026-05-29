from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.features.accounts.models import Account
from app.features.accounts.service import get_account_by_login_identifier, is_temporary_password_expired


async def authenticate_account(db: AsyncSession, username: str, password: str) -> Account | None:
    account = await get_account_by_login_identifier(db, username)
    if account is None or not verify_password(password, account.password_hash):
        return None
    if is_temporary_password_expired(account):
        return None

    return account
