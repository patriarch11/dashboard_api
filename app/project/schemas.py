import datetime
import uuid
from typing import Union

from pydantic import BaseModel


class BaseProject(BaseModel):
    name: str
    start_date: datetime.date
    end_date: datetime.date
    resp_person: str
    summary: str


class Project(BaseProject):
    id: uuid.UUID

    class Config:
        orm_mode = True


class ProjectCreate(BaseProject):
    pass


class ProjectUpdate(BaseModel):
    name: Union[str | None]
    start_date: Union[datetime.date | None]
    end_date: Union[datetime.date | None]
    resp_person: Union[str | None]
    summary: Union[str | None]
