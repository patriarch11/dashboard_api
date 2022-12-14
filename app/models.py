import uuid
from enum import Enum

import ormar
import sqlalchemy

from app.db import MainMeta


# TODO: Set unique id to true

class User(ormar.Model):
    class Meta(MainMeta):
        tablename = "users"

    id: uuid.UUID = ormar.UUID(primary_key=True, unique=True)
    email: str = ormar.String(max_length=30, unique=True)
    avatar: str = ormar.String(max_length=500, nullable=True)
    first_name: str = ormar.String(max_length=50)
    last_name: str = ormar.String(max_length=50)
    password_hash: str = ormar.String(nullable=True, max_length=300)
    is_email_verif: bool = ormar.Boolean(default=False)
    is_active: bool = ormar.Boolean()


class Company(ormar.Model):
    class Meta(MainMeta):
        tablename = "companies"

    id: uuid.UUID = ormar.UUID(primary_key=True, unique=True)
    company_name: str = ormar.String(max_length=100)
    address_1: str = ormar.String(max_length=100, nullable=True)
    address_2: str = ormar.String(max_length=100, nullable=True)
    city: str = ormar.String(max_length=100, nullable=True)
    state: str = ormar.String(max_length=100, nullable=True)
    country: str = ormar.String(max_length=50, nullable=True)
    zip: str = ormar.String(max_length=10, nullable=True)

    owner: User = ormar.ForeignKey(User)


class ContactType(Enum):
    """billing, technical, administrative"""
    billing = "billing"
    technical = "technical"
    administrative = "administrative"


class Contact(ormar.Model):
    class Meta(MainMeta):
        tablename = "contacts"

    id: uuid.UUID = ormar.UUID(primary_key=True, unique=True)
    type: str = ormar.String(max_length=40, choices=ContactType)
    name: str = ormar.String(max_length=50)
    email: str = ormar.String(max_length=100)
    phone_num: str = ormar.String(max_length=30)
    address_1: str = ormar.String(max_length=100)
    address_2: str = ormar.String(max_length=100)
    city: str = ormar.String(max_length=100)
    state: str = ormar.String(max_length=100)
    country: str = ormar.String(max_length=50)
    zip: str = ormar.String(max_length=10)

    company: Company = ormar.ForeignKey(Company)


class Project(ormar.Model):
    class Meta(MainMeta):
        tablename = "projects"

    id: uuid.UUID = ormar.UUID(primary_key=True, unique=True)
    name: str = ormar.String(max_length=70, unique=True)
    start_date: sqlalchemy.Date = ormar.Date()
    end_date: sqlalchemy.Date = ormar.Date()
    resp_person: str = ormar.String(max_length=100)
    summary: str = ormar.String(max_length=300)

    company: Company = ormar.ForeignKey(Company)


class SSHPair(ormar.Model):
    class Meta(MainMeta):
        tablename = "ssh_pairs"

    owner_id: uuid.UUID = ormar.UUID(unique=True)
    gen_date: sqlalchemy.DateTime = ormar.DateTime()
    pair_name: str = ormar.String(max_length=50)
    uuid_: uuid.UUID = ormar.UUID(primary_key=True)
    owner_name: str = ormar.String(max_length=100)
    fp_pub: str = ormar.String(max_length=150)
    fp_prvt: str = ormar.String(max_length=150)
