import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.contacts.routes import contact_router
from app.db import (
    engine,
    metadata,
    database
)
from app.projects.routes import project_router
from app.ssh.routes import ssh_router
from app.users.routes import user_router
from app.companies.routes import company_router
from app.users.auth_routes import auth_router


allowed_cors = [settings.frontend_url, settings.backend_url]

# set up main app
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
app.include_router(contact_router)
app.include_router(project_router)
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


if __name__ == '__main__':
    uvicorn.run('app.main:app', host='localhost', port=8001, reload=True)
