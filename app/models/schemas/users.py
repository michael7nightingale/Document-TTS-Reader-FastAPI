from pydantic import BaseModel, field_validator
from datetime import datetime

from app.services.patterns import check_email


class User:
    _id: str
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_authenticated: bool = True
    is_superuser: bool = False
    is_admin: bool = False


class UserCustomModel(BaseModel):
    """Standard user request model."""
    id: str
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_authenticated: bool = True


class UserRegister(BaseModel):
    username: str
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls, value):
        if not check_email(value):
            raise ValueError("Email is invalid")
        return value


class UserShow(BaseModel):
    username: str
    email: str
    time_created: datetime
