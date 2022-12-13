import uuid
from typing import Union

from pydantic import BaseModel, EmailStr


class BaseContact(BaseModel):
    type: str
    name: str
    email: EmailStr
    phone_num: str
    address_1: str
    address_2: str
    city: str
    state: str
    country: str
    zip: str


class Contact(BaseContact):
    id: uuid.UUID

    class Config:
        orm_mode = True


class ContactCreate(BaseContact):
    pass


class ContactUpdate(BaseModel):
    type: Union[str | None]
    name: Union[str | None]
    email: Union[EmailStr | None]
    phone_num: Union[str | None]
    address_1: Union[str | None]
    address_2: Union[str | None]
    city: Union[str | None]
    state: Union[str | None]
    country: Union[str | None]
    zip: Union[str | None]
