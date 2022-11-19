import aiofiles as aiofiles
from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File
)
from fastapi.responses import JSONResponse

from app.config import settings
from app.users import schemas
from app.users.auth import get_current_user
from app.users.services import (
    update_user,
    delete_user_,
    get_file_name,
    update_avatar,
    send_email,
    verify_user_email
)
from app.users.tokenizator import (
    create_bearer_token,
    JWTBearer
)

user_router = APIRouter(
    prefix='/users',
    tags=['users']
)


@user_router.get('/me', response_model=schemas.User, dependencies=[Depends(JWTBearer())])  # get user basic data
async def get_my_profile(user: schemas.User = Depends(get_current_user)):
    return user


@user_router.put('/me/update', response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def update_user_profile(
        user_data: schemas.UserUpdate,
        user: schemas.User = Depends(get_current_user)
):
    user_ = await update_user(user_id=user.id, user_data=user_data)
    return user_


@user_router.put('/me/update-avatar', response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def edit_avatar(
        avatar: UploadFile = File(...),
        user: schemas.User = Depends(get_current_user),
):
    file_name = get_file_name(avatar.filename)
    user_ = await update_avatar(user_id=user.id, avatar_path=file_name)
    async with aiofiles.open(file_name, 'wb') as out_file:
        content = await avatar.read()
        await out_file.write(content)
    return user_


@user_router.delete('/delete', dependencies=[Depends(JWTBearer())])
async def delete_user(user: schemas.User = Depends(get_current_user)):
    await delete_user_(user_id=user.id)
    return JSONResponse({
        'msg': status.HTTP_204_NO_CONTENT,
        'detail': 'user is deleted'
    })


@user_router.post('/me/verify-my-email', dependencies=[Depends(JWTBearer())])
async def send_verif_email_msg(user: schemas.User = Depends(get_current_user)):
    token = create_bearer_token(user.id)
    msg = f'{settings.server_host}:{settings.server_port}/users/verify-email?token={token.access_token}'
    await send_email(email=[user.email], message=msg)
    return JSONResponse({
        'msg': status.HTTP_200_OK,
        'detail': 'email has been sent'
    })


@user_router.get('/verify-email')
async def verify_email(token: str):
    await verify_user_email(token)
    return JSONResponse({
        'msg': status.HTTP_200_OK,
        'detail': 'your email is verified'
    })
