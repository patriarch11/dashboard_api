import base64
import json

import requests
from asyncpg import UniqueViolationError
from oauthlib.oauth2 import WebApplicationClient
from passlib.hash import bcrypt
from pydantic import EmailStr
from starlette.requests import Request

from app import models
from app.company.schemas import CompanyCreate
from app.company.service import CompanyService
from app.config import settings
from app.user import schemas
from app.user.exceptions import (
    UNIQUE_USER_EMAIL_EXCEPTION,
    CREDENTIALS_EXCEPTION,
    INACTIVE_USER_EXCEPTION
    )
from app.user.tokenizator import (
    create_bearer_token,
    validate_token,
    decode_azure_id_token
    )
from app.user.user_service import UserService


async def get_current_user(request: Request) -> schemas.User:
    token = request.headers.get('Authorization').split(' ')[1]
    user = await validate_token(token)
    if user.is_active:
        return user
    raise INACTIVE_USER_EXCEPTION


class AuthService:

    def __init__(self, oauth_token: str = None):
        self.oauth_token = oauth_token
        self.google_auth_client = WebApplicationClient(settings.google_client_id)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.verify(plain_password, hashed_password)
        except Exception:
            raise CREDENTIALS_EXCEPTION

    @staticmethod
    def hash_password(password: str):
        return bcrypt.hash(password)

    @staticmethod
    async def __activate_user(user_id: int) -> None:
        await models.User.objects.filter(id=user_id).update(is_active=True)

    @staticmethod
    async def deactivate_user(user_id: int) -> None:
        await models.User.objects.filter(id=user_id).update(is_active=False)

    @staticmethod
    async def __get_discovery_document(discovery_url: str) -> dict:
        discovery_document = requests.get(discovery_url).json()
        return discovery_document

    @staticmethod
    async def __get_user_by_email(email: str) -> models.User:
        user = await models.User.objects.get_or_none(email=email)
        if not user:
            raise CREDENTIALS_EXCEPTION
        return user

    @staticmethod
    def __filter_user_info(user_info: dict) -> dict:
        """FILTER USER INFO FROM OAUTH PROVIDERS"""
        email = None
        first_name = "default_first_name"
        last_name = "default_last_name"
        try:
            email = user_info["email"]
        except KeyError:
            pass
        if not email:
            email = user_info["preferred_username"]
        try:
            first_name = user_info["family_name"]
            last_name = user_info["given_name"]
            return {"email": email, "first_name": first_name, "last_name": last_name}
        except KeyError:
            pass
        try:
            first_name = user_info["name"].split(" ")[0]
            last_name = user_info["name"].split(" ")[1]
            return {"email": email, "first_name": first_name, "last_name": last_name}
        except KeyError:
            pass
        return {"email": email, "first_name": first_name, "last_name": last_name}

    async def gen_reset_message(self, email: EmailStr) -> str:
        user = await self.__get_user_by_email(email)
        token_ = create_bearer_token(user.id)
        hashed_token = base64.encodebytes(
            token_.access_token.encode()
            )
        return f"Your recovery code is:\n{hashed_token.decode()}"

    async def validate_reset_message(self, code: str, password: str) -> None:
        token = base64.decodebytes(
            code.encode()
            ).decode()
        user = await validate_token(token)
        await self.set_new_pass(user.id, password)

    async def set_new_pass(self, user_id: int, password: str):
        await models.User.objects.filter(id=user_id).update(
            password_hash=self.hash_password(password)
            )

    async def __auth_via_openid(self, user_data: dict) -> schemas.Token:
        user = await models.User.objects.get_or_none(
            email=user_data["email"]
            )

        if not user:
            await UserService().send_email(
                message="Welcome to platops dashboard",
                email=[user_data["email"]]
                )

            try:
                user = await models.User.objects.create(
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    avatar=None,
                    password_hash=None,
                    is_active=True
                    )
                _ = await CompanyService(user.id).create_company(
                    company_data=CompanyCreate(
                        company_name=user.email,
                        address_1=None,
                        address_2=None,
                        city=None,
                        state=None,
                        country=None,
                        zip=None
                        ),
                    user=user
                    )
            except UniqueViolationError:
                raise UNIQUE_USER_EMAIL_EXCEPTION
        await self.__activate_user(user.id)
        return create_bearer_token(user.id)

    async def create_new_user(self, user_data: schemas.UserCreate) -> schemas.Token:
        try:
            user = await models.User.objects.create(
                email=user_data.email,
                avatar=None,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password_hash=self.hash_password(user_data.password_hash),
                is_active=True
                )
            _ = await CompanyService(user.id).create_company(
                company_data=CompanyCreate(
                    company_name=user.email,
                    address_1=None,
                    address_2=None,
                    city=None,
                    state=None,
                    country=None,
                    zip=None
                    ),
                user=user
                )
        except UniqueViolationError:
            raise UNIQUE_USER_EMAIL_EXCEPTION
        await UserService().send_email(
            email=[user.email],
            message="Welcome to platops dashboard"
            )
        await self.__activate_user(user.id)
        return create_bearer_token(user.id)

    async def authenticate_user(self, email: str, password: str) -> schemas.Token:
        user = await models.User.objects.get_or_none(email=email)

        if not user:
            raise CREDENTIALS_EXCEPTION

        if not self.verify_password(password, user.password_hash):
            raise CREDENTIALS_EXCEPTION
        await self.__activate_user(user.id)
        return create_bearer_token(user.id)

    async def get_user_via_google(self):
        # Get Google's endpoints from discovery document
        discovery_document = await self.__get_discovery_document(settings.google_discovery_url)
        token_endpoint = discovery_document["token_endpoint"]
        userinfo_endpoint = discovery_document["userinfo_endpoint"]

        # Request access_token from Google
        token_url, headers, body = self.google_auth_client.prepare_token_request(
            token_endpoint,
            redirect_url="postmessage",
            code=self.oauth_token
            )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(settings.google_client_id, settings.google_client_secret)
            )

        self.google_auth_client.parse_request_body_response(json.dumps(token_response.json()))
        # Request user's information from Google
        uri, headers, body = self.google_auth_client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        user_info = dict(userinfo_response.json())
        user_data = self.__filter_user_info(user_info)
        return await self.__auth_via_openid(user_data)

    async def get_user_via_microsoft(self) -> schemas.Token:
        user_info = await decode_azure_id_token(self.oauth_token)
        user_data = self.__filter_user_info(user_info)
        return await self.__auth_via_openid(user_data)
