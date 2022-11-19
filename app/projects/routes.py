from fastapi import (
    APIRouter,
    Depends,
    status
)
from starlette.responses import JSONResponse

from app import models
from app.projects import schemas
from app.projects.services import (
    create_project,
    update_project,
    get_project_,
    get_projects_list,
    project_delete
)
from app.users.auth import get_current_user
from app.users.schemas import User
from app.users.tokenizator import JWTBearer

project_router = APIRouter(
    prefix='/projects',
    tags=['projects']
)


@project_router.post('/create', response_model=models.Project, dependencies=[Depends(JWTBearer())])
async def create_new_project(
        project_data: schemas.ProjectCreate,
        company_id: int,
        user: User = Depends(get_current_user)
):
    return await create_project(
        company_id=company_id,
        user_id=user.id,
        project_data=project_data
    )


@project_router.put('/{project_id}', response_model=models.Project, dependencies=[Depends(JWTBearer())])
async def edit_project(
        project_id: int,
        company_id: int,
        project_data: schemas.ProjectUpdate,
        user: User = Depends(get_current_user)
):
    return await update_project(
        company_id=company_id,
        project_id=project_id,
        user_id=user.id,
        project_data=project_data
    )


@project_router.get('/{project_id}', response_model=models.Project, dependencies=[Depends(JWTBearer())])
async def get_project(
        project_id: int,
        company_id: int,
        user: User = Depends(get_current_user)
):
    return await get_project_(
        company_id=company_id,
        project_id=project_id,
        user_id=user.id
    )


@project_router.get('/', response_model=list[models.Project], dependencies=[Depends(JWTBearer())])
async def get_projects(
        company_id: int,
        user: User = Depends(get_current_user)
):
    return await get_projects_list(
        company_id=company_id,
        user_id=user.id
    )


@project_router.delete('/{project_id}', dependencies=[Depends(JWTBearer())])
async def delete_project(
        project_id: int,
        company_id: int,
        user: User = Depends(get_current_user)
):
    await project_delete(
        company_id=company_id,
        user_id=user.id,
        project_id=project_id
    )
    return JSONResponse({
        'msg': status.HTTP_204_NO_CONTENT,
        'detail': 'project is deleted'
    })
