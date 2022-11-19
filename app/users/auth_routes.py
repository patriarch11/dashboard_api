from fastapi import (
    APIRouter,
    Depends
)
from starlette.requests import Request

from app.users import schemas
from app.users.auth import (
    create_new_user,
    authenticate_user,
    get_current_user,
    deactivate_user, get_user_via_google, get_user_via_microsoft,
)
from app.users.tokenizator import JWTBearer

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.get('/google-callback', response_model=schemas.Token)
async def auth_via_google(request: Request):
    code = request.query_params.get('code')
    return await get_user_via_google(code)


@auth_router.post('/azure-callback', response_model=schemas.Token)
async def auth_via_microsoft(request: Request):
    id_token = request.query_params.get('raw_id_token')
    return await get_user_via_microsoft(id_token)


@auth_router.post('/register', response_model=schemas.Token)
async def register_new_user(user_data: schemas.UserCreate):
    return await create_new_user(user_data)


@auth_router.post('/', response_model=schemas.Token)
async def auth(user_data: schemas.UserAuth):
    return await authenticate_user(email=user_data.email, password=user_data.password)


@auth_router.post('/logout', dependencies=[Depends(JWTBearer())])
async def logout(user: schemas.User = Depends(get_current_user)):
    await deactivate_user(user.id)
    return {'msg': 'user is deactivated'}
