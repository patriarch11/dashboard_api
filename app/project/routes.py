import uuid

from fastapi import (
    APIRouter,
    Depends,
    status
    )
from fastapi.responses import JSONResponse

from app.project import schemas
from app.project.service import ProjectService
from app.user.tokenizator import JWTBearer

project_router = APIRouter(
    prefix="/projects",
    tags=["projects"]
    )


@project_router.post("/create", response_model=schemas.Project, dependencies=[Depends(JWTBearer())])
async def create_project(
        project_data: schemas.ProjectCreate,
        company_id: uuid.UUID,
        ):
    return await ProjectService(company_id=company_id).create_project(project_data)


@project_router.get("/", response_model=list[schemas.Project], dependencies=[Depends(JWTBearer())])
async def get_projects_list(company_id: uuid.UUID):
    return await ProjectService(company_id=company_id).get_projects_list()


@project_router.get("/{project_id}", response_model=schemas.Project, dependencies=[Depends(JWTBearer())])
async def get_project(
        project_id: uuid.UUID,
        ):
    return await ProjectService(
        project_id=project_id
        ).get_project()


@project_router.put("/{project_id}", response_model=schemas.Project, dependencies=[Depends(JWTBearer())])
async def update_project(
        project_id: uuid.UUID,
        project_data: schemas.ProjectUpdate
        ):
    return await ProjectService(
        project_id=project_id
        ).update_project(project_data)


@project_router.delete("/project_id", dependencies=[Depends(JWTBearer())])
async def delete_project(
        project_id: uuid.UUID,
        company_id: uuid.UUID
        ):
    await ProjectService(
        company_id=company_id,
        project_id=project_id
        ).delete_project()
    return JSONResponse(
        {
            "msg": status.HTTP_204_NO_CONTENT,
            "details": "project has been deleted"
            }
        )
