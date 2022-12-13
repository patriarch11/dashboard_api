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
from app.user import schemas
from app.user.auth_service import get_current_user
from app.user.tokenizator import JWTBearer, create_bearer_token
from app.user.user_service import UserService

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
    )


@user_router.get("/me", response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def get_my_profile(user: schemas.User = Depends(get_current_user)):
    return user


@user_router.put("/me/update", response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def update_user_profile(
        user_data: schemas.UserUpdate,
        user: schemas.User = Depends(get_current_user)
        ):
    return await UserService(user.id).update_user(user_data)


@user_router.put("/me/update-avatar", response_model=schemas.User, dependencies=[Depends(JWTBearer())])
async def edit_avatar(
        avatar: UploadFile = File(...),
        user: schemas.User = Depends(get_current_user)
        ):
    service = UserService(user.id)
    file_name = service.get_file_name(avatar.filename)
    async with aiofiles.open(file_name, 'wb') as out_file:
        content = await avatar.read()
        await out_file.write(content)
    return await service.update_avatar(file_name)


@user_router.delete("/delete", dependencies=[Depends(JWTBearer())])
async def delete_user(user: schemas.User = Depends(get_current_user)):
    await UserService(user.id).delete_user_()
    return JSONResponse(
        {
            "msg": status.HTTP_204_NO_CONTENT,
            "details": "user is deleted"
            }
        )


@user_router.post("/me/verify-my-email", dependencies=[Depends(JWTBearer())])
async def send_verif_email_msg(user: schemas.User = Depends(get_current_user)):
    token = create_bearer_token(user.id)
    msg = f"{settings.server_host}:{settings.server_port}/users/verify-email?token={token.access_token}"
    await UserService().send_email(email=[user.email], message=msg)
    return JSONResponse(
        {
            "msg": status.HTTP_200_OK,
            "details": "email has been sent"
            }
        )


@user_router.get("/verify-email")
async def verify_email(token: str):
    await UserService().verify_user_email(token)
    return JSONResponse(
        {
            "msg": status.HTTP_200_OK,
            "details": "your email is verified"
            }
        )
