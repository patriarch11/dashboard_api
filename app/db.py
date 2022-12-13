import databases
import sqlalchemy
import ormar

from app.config import settings

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.db_url)
engine = sqlalchemy.create_engine(settings.db_url)


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = database
