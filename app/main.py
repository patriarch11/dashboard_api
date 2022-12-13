from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.company.routes import company_router
from app.config import settings
from app.contact.routes import contact_router
from app.db import (
    database,
    engine,
    metadata
    )
from app.project.routes import project_router
from app.ssh.routes import ssh_router
from app.user.auth_routes import auth_router
from app.user.routes import user_router

allowed_cors = [settings.frontend_url, settings.backend_url]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.mount('/avatars', StaticFiles(directory='avatars'), name='avatars')
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(company_router)
app.include_router(project_router)
app.include_router(contact_router)
app.include_router(ssh_router)

app.state.database = database
metadata.create_all(engine)


@app.on_event('startup')
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event('shutdown')
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()
