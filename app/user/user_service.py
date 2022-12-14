import os
import uuid

import jwt
from fastapi_mail import (
    MessageSchema,
    ConnectionConfig,
    FastMail
    )
from jwt import PyJWTError

from app import models
from app.company.service import CompanyService
from app.config import settings
from app.user import schemas
from app.user.exceptions import CREDENTIALS_EXCEPTION


class UserService:
    config = ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_FROM_NAME=settings.mail_from_name,
        USE_CREDENTIALS=settings.use_credentials,
        VALIDATE_CERTS=settings.validate_credentials,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,

        )

    fastapi_mail = FastMail(config=config)

    @staticmethod
    def get_file_name(file_name: str) -> str:
        """CREATE FILENAME FOR USERS AVATARS"""
        ext = file_name.strip().split(".")[1]
        file_name = f'{uuid.uuid4()}.{ext}'
        return os.path.join('avatars/', file_name)

    @staticmethod
    async def get_user_by_email(email: str) -> models.User:
        user = await models.User.objects.get_or_none(email=email)
        if not user:
            raise CREDENTIALS_EXCEPTION
        return user

    @staticmethod
    async def send_email(email: schemas.EmailSchema, message: str) -> None:
        """SEND MAIL"""
        message = MessageSchema(
            subject_line=settings.mail_subject_line,
            recipients=email,
            body=message,
            subtype='plain'
            )
        await UserService.fastapi_mail.send_message(message)

    @staticmethod
    async def verify_user_email(token: str) -> None:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
                )
        except PyJWTError:
            raise CREDENTIALS_EXCEPTION
        await models.User.objects.filter(id=uuid.UUID(payload["sub"])).update(is_email_verif=True)

    def __init__(self, user_id: uuid.UUID = None):
        self.user_id = user_id

    async def update_user(self, user_data: schemas.UserUpdate) -> schemas.User:
        new_data = dict()
        is_email_verif = True

        for key, value in user_data.dict().items():
            if value:
                new_data[key] = value
        try:
            if new_data["email"]:
                is_email_verif = False
        except KeyError:
            pass

        await models.User.objects.filter(id=self.user_id).update(
            **new_data,
            is_email_verif=is_email_verif
            )
        user = await models.User.objects.filter(id=self.user_id).first()
        return schemas.User.parse_obj(user)

    async def update_avatar(self, avatar_path: str) -> schemas.User:
        await models.User.objects.filter(id=self.user_id).update(avatar=avatar_path)
        user = await models.User.objects.filter(id=self.user_id).first()
        return schemas.User.parse_obj(user)

    async def delete_user_(self) -> None:
        # TODO: make cascade delete
        id_list = []
        companies = await CompanyService(user_id=self.user_id).get_list_companies()
        for company in companies:
            id_list.append(company.id)
        for id_ in id_list:
            await CompanyService(user_id=self.user_id, company_id=id_).delete_company()
        id_list.clear()
        await models.User.objects.clear(id=self.user_id)
