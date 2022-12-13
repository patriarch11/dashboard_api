import uuid
from typing import (
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    EmailStr
)


class BaseUser(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(BaseUser):
    password_hash: str


class User(BaseUser):
    id: uuid.UUID
    avatar: Optional[str]
    is_email_verif: bool
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Union[EmailStr | None]
    first_name: Union[str | None]
    last_name: Union[str | None]


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserPassReset(BaseModel):
    code: str
    password: str


class EmailSchema(BaseModel):
    email: list[EmailStr]


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
