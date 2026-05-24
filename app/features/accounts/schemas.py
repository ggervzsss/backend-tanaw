from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.features.accounts.options import ENTERPRISE_CATEGORIES, SAN_PEDRO_ADDRESS_SUFFIX, SAN_PEDRO_BARANGAYS


class AuthUser(BaseModel):
    id: str
    email: str
    displayName: str
    role: str
    title: str
    mustChangePassword: bool = False
    enterpriseId: str | None = None
    enterpriseName: str | None = None


class LguAccountCreate(BaseModel):
    firstName: str = Field(min_length=1, max_length=60)
    lastName: str = Field(min_length=1, max_length=60)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    role: Literal["admin", "it", "staff"]


class EnterpriseAccountCreate(BaseModel):
    enterpriseName: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=120)
    managerName: str = Field(min_length=1, max_length=120)
    email: EmailStr
    contactNumber: str | None = Field(default=None, max_length=40)
    barangay: str = Field(min_length=1, max_length=120)
    address: str = Field(min_length=1, max_length=255)
    enterpriseId: str | None = Field(default=None, max_length=120)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ENTERPRISE_CATEGORIES:
            raise ValueError("Enterprise category is not supported.")
        return normalized

    @field_validator("barangay")
    @classmethod
    def validate_barangay(cls, value: str) -> str:
        normalized = value.strip().lower()
        for barangay in SAN_PEDRO_BARANGAYS:
            if barangay.lower() == normalized:
                return barangay
        raise ValueError("Barangay is not supported.")

    @field_validator("address")
    @classmethod
    def normalize_address(cls, value: str) -> str:
        address = value.strip().rstrip(",")
        if not address:
            raise ValueError("Address is required.")
        if address.lower().endswith(SAN_PEDRO_ADDRESS_SUFFIX.lower()):
            return address
        return f"{address}, {SAN_PEDRO_ADDRESS_SUFFIX}"


class AccountSummary(BaseModel):
    id: str
    email: str
    phone: str | None
    firstName: str | None
    lastName: str | None
    enterpriseName: str | None
    category: str | None
    managerName: str | None
    barangay: str | None
    address: str | None
    enterpriseId: str | None
    gatewayStatus: str | None
    displayName: str
    role: str
    title: str
    status: str
    mustChangePassword: bool
    createdAt: datetime
    lastLoginAt: datetime | None


class AccountStatusUpdate(BaseModel):
    status: Literal["active", "inactive"]


class DeliverySummary(BaseModel):
    id: str
    accountId: str
    channel: str
    recipient: str
    subject: str
    body: str
    status: str
    createdAt: datetime


class PasswordChangeRequest(BaseModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8, max_length=128)
