from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AccountRole(StrEnum):
    IT = "it"
    ADMIN = "admin"
    STAFF = "staff"
    ENTERPRISE = "enterprise"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    enterprise_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    manager_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    barangay: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enterprise_id: Mapped[str | None] = mapped_column(String(120), unique=True, index=True, nullable=True)
    gateway_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    gateway_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[AccountRole] = mapped_column(Enum(AccountRole, name="account_role"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus, name="account_status"), nullable=False, default=AccountStatus.ACTIVE)
    must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    temporary_password_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    temporary_password_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DeliveryChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"


class DeliveryStatus(StrEnum):
    RECORDED = "recorded"
    SENT = "sent"
    FAILED = "failed"


class DevDelivery(Base):
    __tablename__ = "dev_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    account_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    channel: Mapped[DeliveryChannel] = mapped_column(Enum(DeliveryChannel, name="delivery_channel"), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus, name="delivery_status"), nullable=False, default=DeliveryStatus.RECORDED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
