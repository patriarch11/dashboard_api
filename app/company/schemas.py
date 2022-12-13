import uuid
from typing import Union

from pydantic import BaseModel


class BaseCompany(BaseModel):
    company_name: str
    address_1: str | None
    address_2: str | None
    city: str | None
    state: str | None
    country: str | None
    zip: str | None


class Company(BaseCompany):
    id: uuid.UUID

    class Config:
        orm_mode = True


class CompanyCreate(BaseCompany):
    pass


class CompanyUpdate(BaseCompany):
    company_name: Union[str | None]
    address_1: Union[str | None]
    address_2: Union[str | None]
    city: Union[str | None]
    state: Union[str | None]
    country: Union[str | None]
    zip: Union[str | None]

