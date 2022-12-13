import uuid

from asyncpg.exceptions import UniqueViolationError
from fastapi import (
    HTTPException,
    status
    )

from app import models
from app.project import schemas


class ProjectService:

    def __init__(self,
                 company_id: uuid.UUID = None,
                 project_id: uuid.UUID = None
                 ):
        self.company_id = company_id,
        self.project_id = project_id

    async def create_project(self, project_data: schemas.ProjectCreate) -> schemas.Project:
        try:
            project = await models.Project.objects.create(
                **project_data.dict(),
                company=self.company_id[0]
                )
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Project with same name is already exists"
                )
        return schemas.Project.parse_obj(project)

    async def get_project(self) -> schemas.Project:
        # TODO: check for needles company_id
        try:
            project = await models.Project.objects.filter(
                id=self.project_id,
                company=self.company_id[0]
                ).first()
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return schemas.Project.parse_obj(project)

    async def get_projects_list(self) -> list[schemas.Project]:
        projects = await models.Project.objects.filter(
            company=self.company_id[0]
            ).all()
        return [schemas.Project.parse_obj(project) for project in projects]

    async def update_project(self, project_data) -> schemas.Project:
        new_data = dict()

        for key, value in project_data.dict().items():
            if value:
                new_data[key] = value
        # TODO: Check for needless of try block
        try:
            await models.Project.objects.filter(
                id=self.project_id,
                company=self.company_id
                ).update(**new_data)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        project = await self.get_project()
        return schemas.Project.parse_obj(project)

    async def delete_project(self) -> None:
        await models.Project.objects.delete(
            id=self.project_id,
            company=self.company_id
            )
