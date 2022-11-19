from fastapi import (
    HTTPException,
    status
)

from app import models
from app.companies import schemas


async def company_create(user_id: int, company_data: schemas.CompanyCreate) -> schemas.Company:
    user = await models.User.objects.filter(id=user_id).first()
    company = await models.Company.objects.create(
        **company_data.dict(),
        owner=user
    )
    return schemas.Company.parse_obj(company)


async def get_list_companies(user_id: int) -> list[schemas.Company]:
    companies = await models.Company.objects.filter(owner=user_id).all()
    return [schemas.Company.parse_obj(company) for company in companies]


async def get_company(
        company_id: int,
        user_id: int
) -> schemas.Company:
    try:
        company = await models.Company.objects.filter(id=company_id, owner=user_id).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

    return schemas.Company.parse_obj(company)


async def update_company_(
        company_id: int,
        user_id: int,
        company_data: schemas.CompanyUpdate
) -> schemas.Company:

    new_data = dict()

    for key, value in company_data.dict().items():
        if value:
            new_data[key] = value

    await models.Company.objects.filter(
        id=company_id,
        owner=user_id
    ).update(**new_data)

    return await get_company(company_id, user_id)


async def company_delete(company_id: int, user_id: int) -> None:
    await models.Contact.objects.delete(company=company_id)
    await models.Project.objects.delete(company=company_id)
    await models.Company.objects.delete(id=company_id, owner=user_id)
