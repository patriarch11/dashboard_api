import datetime
import uuid

from pydantic import BaseModel


class SSHPair(BaseModel):
    gen_date: datetime.datetime
    pair_name: str
    fp_pub: str
    fp_prvt: str
    uuid_: uuid.UUID

    class Config:
        orm_mode = True

