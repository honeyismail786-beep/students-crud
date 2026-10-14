from datetime import date
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

PHONE_PATTERN = r"^\+?[0-9]{10,15}$"


class StudentBase(BaseModel):
    name: str = Field(..., max_length=100, examples=["Asha Rao"])
    date_of_birth: date = Field(..., examples=["2005-04-12"])
    email: Optional[EmailStr] = Field(None, examples=["asha@example.com"])
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN, examples=["9876543210"])
    course: Optional[str] = Field(None, max_length=100, examples=["B.Tech CSE"])
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("name must be at least 2 characters")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_in_future(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v

    @model_validator(mode="after")
    def need_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("provide at least one contact: email or phone")
        return self


class StudentCreate(StudentBase):
    """Body for creating a student."""


class StudentUpdate(BaseModel):
    """Body for updating a student. Every field is optional."""

    name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=PHONE_PATTERN)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> str:
        if v is None:
            raise ValueError("name cannot be null")
        v = v.strip()
        if len(v) < 2:
            raise ValueError("name must be at least 2 characters")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_in_future(cls, v: Optional[date]) -> date:
        if v is None:
            raise ValueError("date_of_birth cannot be null")
        if v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v


class StudentOut(BaseModel):
    """Shape of a student returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None