from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException
)
from starlette.responses import JSONResponse

from app import models
from app.contacts import schemas
from app.contacts.services import (
    create_contact,
    update_contact,
    get_contact_list,
    get_contact_,
    delete_contact_
)
from app.users.auth import get_current_user
from app.users.schemas import User
from app.users.tokenizator import JWTBearer

contact_router = APIRouter(
    prefix='/contacts',
    tags=['contacts']
)


@contact_router.post('/add', response_model=models.Contact, dependencies=[Depends(JWTBearer())])
async def add_contact(
        contact_data: schemas.ContactCreate,
        company_id: int,
        user: User = Depends(get_current_user)
):
    try:
        contact = await create_contact(
            user_id=user.id,
            company_id=company_id,
            contact_data=contact_data
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return contact


@contact_router.put('/update{contact_id}', response_model=models.Contact, dependencies=[Depends(JWTBearer())])
async def edit_contact(
        contact_id: int,
        contact_data: schemas.ContactUpdate,
        company_id: int,
        user: User = Depends(get_current_user)
):
    try:
        contact = await update_contact(
            contact_data=contact_data,
            user_id=user.id,
            company_id=company_id,
            contact_id=contact_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return contact


@contact_router.get('/list', response_model=list[models.Contact], dependencies=[Depends(JWTBearer())])
async def get_contacts(company_id: int, user: User = Depends(get_current_user)):
    return await get_contact_list(company_id=company_id, user_id=user.id)


@contact_router.get('/{contact_id}', response_model=models.Contact, dependencies=[Depends(JWTBearer())])
async def get_contact(
        contact_id: int,
        company_id: int,
        user: User = Depends(get_current_user)
):
    try:
        contact = await get_contact_(
            user_id=user.id,
            contact_id=contact_id,
            company_id=company_id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return contact


@contact_router.delete('/{contact_id}', dependencies=[Depends(JWTBearer())])
async def delete_contact(
        contact_id: int,
        company_id: int,
        user: User = Depends(get_current_user)
):
    try:
        await delete_contact_(
            contact_id=contact_id,
            company_id=company_id,
            user_id=user.id
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse({
        'msg': status.HTTP_204_NO_CONTENT,
        'detail': 'contact is deleted'
    })
