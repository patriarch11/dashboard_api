from fastapi import (
    APIRouter,
    Depends,
    status
    )
from pydantic import EmailStr
from starlette.requests import Request
from fastapi.responses import JSONResponse

from app.user import schemas
from app.user.auth_service import AuthService, get_current_user
from app.user.tokenizator import JWTBearer
from app.user.user_service import UserService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/google-callback", response_model=schemas.Token)
async def auth_via_google(request: Request):
    return await AuthService(
        oauth_token=request.query_params.get("code")
        ).get_user_via_google()


@auth_router.post("/azure-callback", response_model=schemas.Token)
async def auth_via_microsoft(request: Request):
    return await AuthService(
        oauth_token=request.query_params.get("raw_id_token")
        ).get_user_via_microsoft()


@auth_router.post("/register", response_model=schemas.Token)
async def register_new_user(user_data: schemas.UserCreate):
    return await AuthService().create_new_user(user_data)


@auth_router.post("/", response_model=schemas.Token)
async def auth(user_data: schemas.UserAuth):
    return await AuthService().authenticate_user(
        user_data.email,
        user_data.password
        )


@auth_router.post("/logout", dependencies=[Depends(JWTBearer())])
async def logout(user: schemas.User = Depends(get_current_user)):
    await AuthService().deactivate_user(user.id)
    return {'msg': 'user is deactivated'}


@auth_router.post("/start-reset-password")
async def send_reset_mail(email: EmailStr):
    await UserService().send_email(
        [email],
        await AuthService().gen_reset_message(email)
        )
    return JSONResponse(
        {
            "msg": status.HTTP_200_OK,
            "details": "Recovery code has been sent on your email address"
            }
        )


@auth_router.post("/reset-password")
async def set_new_password(user: schemas.UserPassReset):
    await AuthService().validate_reset_message(user.code, user.password)
    return JSONResponse(
        {
            "msg": status.HTTP_200_OK,
            "details": "New password set success"
            }
        )
