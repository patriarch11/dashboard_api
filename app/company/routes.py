import uuid

from fastapi import (
    APIRouter,
    Depends,
    status
    )
from starlette.responses import JSONResponse

from app.company import schemas
from app.company.service import CompanyService
from app.user.auth_service import get_current_user
from app.user.schemas import User
from app.user.tokenizator import JWTBearer

company_router = APIRouter(
    prefix="/companies",
    tags=["companies"]
    )


@company_router.post("/create", response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def create_company(
        company_data: schemas.CompanyCreate,
        user=Depends(get_current_user)
        ):
    return await CompanyService().create_company(company_data, user)


@company_router.get("/list", response_model=list[schemas.Company], dependencies=[Depends(JWTBearer())])
async def get_user_companies(user: User = Depends(get_current_user)):
    return await CompanyService(user_id=user.id).get_list_companies()


@company_router.get("/{company_id}", response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def get_company(
        company_id: uuid.UUID,
        user: User = Depends(get_current_user)
        ):
    return await CompanyService(user.id, company_id).get_company()


@company_router.put("/{company_id}", response_model=schemas.Company, dependencies=[Depends(JWTBearer())])
async def update_company(
        company_id: uuid.UUID,
        company_data: schemas.CompanyUpdate,
        user: User = Depends(get_current_user)
        ):
    return await CompanyService(user.id, company_id).update_company(company_data)


@company_router.delete("/company_id", dependencies=[Depends(JWTBearer())])
async def delete_company(
        company_id: uuid.UUID,
        user: User = Depends(get_current_user)
        ):
    await CompanyService(user.id, company_id).delete_company()
    return JSONResponse(
        {
            "msg": status.HTTP_204_NO_CONTENT,
            "details": "company has been deleted"
            }
        )
