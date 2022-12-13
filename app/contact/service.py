import uuid

from app import models
from app.contact import schemas


class ContactService:

    def __init__(self, company_id: uuid.UUID = None, contact_id: uuid.UUID = None):
        self.company_id = company_id,
        self.contact_id = contact_id

    async def create_contact(self, contact_data: schemas.ContactCreate) -> schemas.Contact:
        contact = await models.Contact.objects.create(
            **contact_data.dict(),
            company=self.company_id[0]
            )
        return schemas.Contact.parse_obj(contact)

    async def get_contact(self):
        return await models.Contact.objects.filter(
            id=self.contact_id
            ).first()

    async def get_contacts_list(self) -> list[schemas.Contact]:
        return await models.Contact.objects.filter(
            company=self.company_id[0]
            ).all()

    async def update_contact(self, contact_data: schemas.ContactUpdate) -> schemas.Contact:
        new_data = dict()

        for key, value in contact_data.dict().items():
            if value:
                new_data[key] = value

        await models.Contact.objects.filter(
            id=self.contact_id,
            company=self.company_id[0]
            ).update(**new_data)

        return await self.get_contact()

    async def delete_contact(self) -> None:
        await models.Contact.objects.delete(
            id=self.contact_id
            )
