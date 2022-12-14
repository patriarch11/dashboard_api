import uuid

from fastapi import (
    HTTPException,
    status
    )

from app import models
from app.company import schemas


class CompanyService:

    def __init__(self, user_id: uuid.UUID = None, company_id: uuid.UUID = None):
        self.user_id = user_id
        self.company_id = company_id

    @staticmethod
    async def create_company(company_data: schemas.CompanyCreate, user: models.User) -> schemas.Company:
        # TODO: refactor getting user from db
        user = await models.User.objects.filter(id=user.id).first()
        company = await models.Company.objects.create(
            id=uuid.uuid4(),
            **company_data.dict(),
            owner=user
            )
        return schemas.Company.parse_obj(company)

    async def get_list_companies(self) -> list[schemas.Company]:
        companies = await models.Company.objects.filter(owner=self.user_id).all()
        return [schemas.Company.parse_obj(company) for company in companies]

    async def get_company(self) -> schemas.Company:
        try:
            company = await models.Company.objects.filter(id=self.company_id, owner=self.user_id).first()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
                )

        return schemas.Company.parse_obj(company)

    async def update_company(self, company_data: schemas.CompanyUpdate) -> schemas.Company:
        new_data = dict()

        for key, value in company_data.dict().items():
            if value:
                new_data[key] = value
        await models.Company.objects.filter(
            id=self.company_id,
            owner=self.user_id
            ).update(**new_data)
        company = await self.get_company()
        return schemas.Company.parse_obj(company)

    async def delete_company(self):
        await models.Contact.objects.delete(company=self.company_id)
        await models.Project.objects.delete(company=self.company_id)
        await models.Company.objects.delete(id=self.company_id, owner=self.user_id)
