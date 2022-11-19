import os
import uuid

import jwt
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema
)
from jwt import PyJWTError

from app.companies.services import (
    get_list_companies,
    company_delete
)
from app.config import settings
from app.users import schemas
from app import models
from app.users.exceptions import CREDENTIALS_EXCEPTION

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


async def get_user_by_email(email: str) -> models.User:
    user = await models.User.objects.get_or_none(email=email)
    if not user:
        raise CREDENTIALS_EXCEPTION
    return user


async def update_user(user_id: int, user_data: schemas.UserUpdate) -> schemas.User:
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

    await models.User.objects.filter(id=user_id).update(
        **new_data,
        is_email_verif=is_email_verif
    )
    user = await models.User.objects.filter(id=user_id).first()
    return schemas.User.parse_obj(user)


async def update_avatar(user_id: int, avatar_path: str) -> schemas.User:
    await models.User.objects.filter(id=user_id).update(avatar=avatar_path)
    user = await models.User.objects.filter(id=user_id).first()
    return schemas.User.parse_obj(user)


async def delete_user_(user_id: int) -> None:
    id_list = []
    companies = await get_list_companies(user_id=user_id)
    for company in companies:
        id_list.append(company.id)
    for id_ in id_list:
        await company_delete(company_id=id_, user_id=user_id)
    id_list.clear()
    await models.User.objects.delete(id=user_id)


async def send_email(email: schemas.EmailSchema, message: str) -> None:
    """SEND MAIL"""
    message = MessageSchema(
        subject_line=settings.mail_subject_line,
        recipients=email,
        body=message,
        subtype='plain'
    )
    await fastapi_mail.send_message(message)


def get_file_name(file_name: str) -> str:
    """CREATE FILENAME FOR USERS AVATARS"""
    ext = file_name.strip().split('.')[1]
    file_name = f'{uuid.uuid4()}.{ext}'
    return os.path.join('avatars/', file_name)


async def verify_user_email(token: str) -> None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
    except PyJWTError:
        raise CREDENTIALS_EXCEPTION

    await models.User.objects.filter(id=payload['sub']).update(is_email_verif=True)
