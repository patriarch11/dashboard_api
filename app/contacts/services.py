from app import models
from app.companies.services import get_company
from app.contacts import schemas


async def create_contact(
        user_id: int,
        company_id: int,
        contact_data: schemas.ContactCreate
) -> models.Contact:
    company = await get_company(user_id=user_id, company_id=company_id)

    contact = await models.Contact.objects.create(
        **contact_data.dict(),
        company=company.dict()['id']
    )
    return contact


async def get_contact_(user_id: int, company_id: int, contact_id: int) -> models.Contact:
    company = await get_company(user_id=user_id, company_id=company_id)

    contact = await models.Contact.objects.filter(
        id=contact_id,
        company=company.dict()['id']
    ).first()
    return contact


async def get_contact_list(user_id: int, company_id: int) -> list[models.Contact]:
    company = await get_company(user_id=user_id, company_id=company_id)

    contacts = await models.Contact.objects.filter(
        company=company.dict()['id']
    ).all()

    return contacts


async def update_contact(
        contact_id: int,
        user_id: int,
        company_id: int,
        contact_data: schemas.ContactUpdate

) -> models.Contact:
    company = await get_company(user_id=user_id, company_id=company_id)

    new_data = dict()

    for key, value in contact_data.dict().items():
        if value:
            new_data[key] = value

    await models.Contact.objects.filter(
        id=contact_id,
        company=company.dict()['id']
    ).update(**new_data)

    return await get_contact_(user_id, company_id, contact_id)


async def delete_contact_(
        contact_id: int,
        company_id: int,
        user_id: int

) -> None:
    company = await get_company(user_id=user_id, company_id=company_id)

    await models.Contact.objects.delete(
        id=contact_id,
        company=company.dict()['id']
    )
