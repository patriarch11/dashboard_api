import uuid

from fastapi import (
    APIRouter,
    Depends,
    status,
    )
from fastapi.responses import JSONResponse

from app.contact import schemas
from app.contact.service import ContactService
from app.user.tokenizator import JWTBearer

contact_router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
    )


@contact_router.post("/add", response_model=schemas.Contact, dependencies=[Depends(JWTBearer())])
async def add_contact(company_id: uuid.UUID, contact_data: schemas.ContactCreate):
    return await ContactService(company_id=company_id).create_contact(contact_data)


@contact_router.get("/{contact_id}", response_model=schemas.Contact, dependencies=[Depends(JWTBearer())])
async def get_contact(contact_id: uuid.UUID):
    return await ContactService(contact_id=contact_id).get_contact()


# /list
@contact_router.get("/", response_model=list[schemas.Contact], dependencies=[Depends(JWTBearer())])
async def get_list_contacts(company_id: uuid.UUID):
    return await ContactService(company_id=company_id).get_contacts_list()


@contact_router.put("/update{contact_id}", response_model=schemas.Contact, dependencies=[Depends(JWTBearer())])
async def update_contact(contact_id: uuid.UUID, contact_data: schemas.ContactUpdate):
    return await ContactService(contact_id=contact_id).update_contact(contact_data)


@contact_router.delete("/{contact_id}", dependencies=[Depends(JWTBearer())])
async def delete_contact(contact_id: uuid.UUID):
    await ContactService(contact_id=contact_id).delete_contact()
    return JSONResponse(
        {
            "msg": status.HTTP_204_NO_CONTENT,
            "details": "contact has been deleted"
            }
        )
