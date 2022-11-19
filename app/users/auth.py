import json

import requests
from asyncpg import UniqueViolationError
from oauthlib.oauth2 import WebApplicationClient
from passlib.hash import bcrypt
from starlette.requests import Request

from app.config import settings
from app.companies.services import company_create
from app.companies.schemas import CompanyCreate
from app.users.exceptions import (
    CREDENTIALS_EXCEPTION,
    UNIQUE_USER_EMAIL_EXCEPTION,
    INACTIVE_USER_EXCEPTION
)
from app.users import schemas
from app import models
from app.users.services import send_email
from app.users.tokenizator import (
    create_bearer_token,
    validate_token, decode_azure_id_token
)


async def get_current_user(request: Request) -> schemas.User:
    token = request.headers.get('Authorization').split(' ')[1]
    user = await validate_token(token)
    if user.is_active:
        return user
    raise INACTIVE_USER_EXCEPTION


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except Exception:
        raise CREDENTIALS_EXCEPTION


def hash_password(password: str):
    return bcrypt.hash(password)


async def activate_user(user_id: int) -> None:
    await models.User.objects.filter(id=user_id).update(is_active=True)


async def deactivate_user(user_id: int) -> None:
    await models.User.objects.filter(id=user_id).update(is_active=False)


async def create_new_user(user_data: schemas.UserCreate) -> schemas.Token:
    try:
        user = await models.User.objects.create(
            email=user_data.email,
            avatar=None,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hash_password(user_data.password_hash),
            is_active=True
        )
        company_data = CompanyCreate(
            company_name=user.email,
            address_1=None,
            address_2=None,
            city=None,
            state=None,
            country=None,
            zip=None
        )
        company = await company_create(user_id=user.id, company_data=company_data)
    except UniqueViolationError:
        raise UNIQUE_USER_EMAIL_EXCEPTION
    await send_email(
        email=[user.email],
        message='Welcome to platops dashboard'
    )
    await activate_user(user.id)
    return create_bearer_token(user.id)


async def authenticate_user(email: str, password: str) -> schemas.Token:
    user = await models.User.objects.get_or_none(email=email)

    if not user:
        raise CREDENTIALS_EXCEPTION

    if not verify_password(password, user.password_hash):
        raise CREDENTIALS_EXCEPTION
    await activate_user(user.id)
    return create_bearer_token(user.id)


async def auth_via_openid(user_data: dict) -> schemas.Token:
    user = await models.User.objects.get_or_none(
        email=user_data['email'],
        password_hash=None
    )

    if not user:
        await send_email(
            message='Welcome to platops dashboard',
            email=[user_data['email']]
        )

        try:
            user = await models.User.objects.create(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                avatar=None,
                password_hash=None,
                is_active=True
            )
            company_data = CompanyCreate(
                company_name=user.email,
                address_1=None,
                address_2=None,
                city=None,
                state=None,
                country=None,
                zip=None
            )
            company = await company_create(user_id=user.id, company_data=company_data)
        except UniqueViolationError:
            raise UNIQUE_USER_EMAIL_EXCEPTION
    await activate_user(user.id)
    return create_bearer_token(user.id)


"""GOOGLE & AZURE AUTH"""

GOOGLE_AUTH_CLIENT = WebApplicationClient(settings.google_client_id)


async def get_discovery_document(discovery_url: str) -> dict:
    discovery_document = requests.get(discovery_url).json()
    return discovery_document


async def get_user_via_google(code: str) -> schemas.Token:
    # Get Google's endpoints from discovery document
    discovery_document = await get_discovery_document(settings.google_discovery_url)
    token_endpoint = discovery_document["token_endpoint"]
    userinfo_endpoint = discovery_document["userinfo_endpoint"]

    # Request access_token from Google
    token_url, headers, body = GOOGLE_AUTH_CLIENT.prepare_token_request(
        token_endpoint,
        redirect_url='postmessage',
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(settings.google_client_id, settings.google_client_secret)
    )
    GOOGLE_AUTH_CLIENT.parse_request_body_response(json.dumps(token_response.json()))
    # Request user's information from Google
    uri, headers, body = GOOGLE_AUTH_CLIENT.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    user_info = dict(userinfo_response.json())
    user_data = {
        'email': user_info.get('email'),
        'first_name': user_info.get('name').split(' ')[0],
        'last_name': user_info.get('name').split(' ')[1]
    }
    return await auth_via_openid(user_data)


async def get_user_via_microsoft(token: str) -> schemas.Token:
    user_data = await decode_azure_id_token(token)
    return await auth_via_openid(user_data)
