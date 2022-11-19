from app import models
from app.companies.services import get_company
from app.projects import schemas

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status


async def create_project(
        company_id: int,
        user_id: int,
        project_data: schemas.ProjectCreate
) -> models.Project:
    company = await get_company(user_id=user_id, company_id=company_id)

    try:
        project = await models.Project.objects.create(
            **project_data.dict(),
            company=company.dict()['id']
        )
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Project with same name is already exists'
        )
    return project


async def get_project_(
        company_id: int,
        user_id: int,
        project_id: int

) -> models.Project:
    company = await get_company(user_id=user_id, company_id=company_id)

    try:
        project = await models.Project.objects.filter(
            id=project_id,
            company=company.dict()['id']
        ).first()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return project


async def get_projects_list(
        company_id: int,
        user_id: int,

) -> list[models.Project]:
    company = await get_company(user_id=user_id, company_id=company_id)

    projects = await models.Project.objects.filter(
        company=company.dict()['id']
    ).all()
    return projects


async def update_project(
        company_id: int,
        user_id: int,
        project_id: int,
        project_data: schemas.ProjectUpdate

) -> models.Project:
    company = await get_company(user_id=user_id, company_id=company_id)

    new_data = dict()

    for key, value in project_data.dict().items():
        if value:
            new_data[key] = value

    try:
        await models.Project.objects.filter(
            id=project_id,
            company=company.dict()['id']
        ).update(**new_data)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await get_project_(
        company_id=company.dict()['id'],
        user_id=user_id,
        project_id=project_id
    )


async def project_delete(
        company_id: int,
        user_id: int,
        project_id: int,
) -> None:
    company = await get_company(user_id=user_id, company_id=company_id)

    await models.Project.objects.delete(
        id=project_id,
        company=company.dict()['id']
    )
