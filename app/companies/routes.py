from fastapi import (
    APIRouter,
    Depends,
    status
)
from starlette.responses import JSONResponse

from app.companies import schemas
from app.companies.services import (
    company_create,
    get_list_companies,
    update_company_,
    company_delete,
    get_company
)
from app.users.auth import get_current_user
from app.users.schemas import User
from app.users.tokenizator import JWTBearer

company_router = APIRouter(
    prefix='/companies',
    tags=['companies']
)


@company_router.post('/create', response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def create_company(
        company_data: schemas.CompanyCreate,
        user: User = Depends(get_current_user)
):
    company = await company_create(company_data=company_data, user_id=user.id)
    return company


@company_router.get('/list', response_model=list[schemas.Company], dependencies=[Depends(JWTBearer())])
async def get_user_companies(user: User = Depends(get_current_user)):
    return await get_list_companies(user_id=user.id)


@company_router.get('/{company_id}', response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def get_one_company(
        company_id: int,
        user: User = Depends(get_current_user)
):
    return await get_company(
        company_id=company_id,
        user_id=user.id
    )


@company_router.put('/{company_id}', response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def update_company(
        company_id: int,
        company_data: schemas.CompanyUpdate,
        user: User = Depends(get_current_user)
):
    return await update_company_(
        company_id=company_id,
        user_id=user.id,
        company_data=company_data
    )


@company_router.delete('/{company_id}', dependencies=[Depends(JWTBearer())])
async def delete_company(
        company_id: int,
        user: User = Depends(get_current_user)
):
    await company_delete(company_id=company_id, user_id=user.id)
    return JSONResponse({
        'msg': status.HTTP_204_NO_CONTENT,
        'detail': 'company is deleted'
    })
