import uuid

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status
)
from fastapi.responses import Response

from app.ssh.schemas import SSHPair
from app.ssh.ssh_keys import SSHService
from app.user.auth_service import get_current_user
from app.user.schemas import User
from app.user.tokenizator import JWTBearer

ssh_router = APIRouter(prefix='/ssh', tags=['ssh keys'])

"""
TODO: Need total refactoring
"""


@ssh_router.post('/create-ssh', response_model=SSHPair, dependencies=[Depends(JWTBearer())])
async def create_new_ssh_key(
        key_name: str,
        user: User = Depends(get_current_user)
):
    service = SSHService(user.id, user.email)

    ssh_pair = await service.create_ssh_pair(key_name)
    return SSHPair.parse_obj(ssh_pair)


@ssh_router.post('/add-ssh', dependencies=[Depends(JWTBearer())])
async def add_new_ssh(
        key_name: str,
        public_key: UploadFile = File(...),
        private_key: UploadFile = File(...),
        user: User = Depends(get_current_user)
):
    service = SSHService(user.id, user.email)
    # pub, prv = await service.check_key_pair(public_key, private_key)
    return await service.add_ssh_pair(public_key, private_key, key_name)


@ssh_router.get('/my-ssh-keys', response_model=list[SSHPair], dependencies=[Depends(JWTBearer())])
async def get_keys(user: User = Depends(get_current_user)):
    service = SSHService(user.id, user.email)
    ssh_pairs = await service.get_my_keys_info()
    return [SSHPair.parse_obj(pair) for pair in ssh_pairs]


@ssh_router.get('/download-ssh-pub', dependencies=[Depends(JWTBearer())])
async def download_ssh_pub_key(uuid_: uuid.UUID, user: User = Depends(get_current_user)):
    service = SSHService(user.id, user.email)
    file, file_name = await service.download_ssh_key(uuid_, 'public')
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return Response(file, headers=headers)


@ssh_router.get('/download-ssh-prv', dependencies=[Depends(JWTBearer())])
async def download_ssh_prv_key(uuid_: uuid.UUID, user: User = Depends(get_current_user)):
    service = SSHService(user.id, user.email)
    file, file_name = await service.download_ssh_key(uuid_, 'private')
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return Response(file, headers=headers)


@ssh_router.delete('/delete-ssh', dependencies=[Depends(JWTBearer())])
async def delete_ssh_pair(uuid_: uuid.UUID, user: User = Depends(get_current_user)):
    service = SSHService(user.id, user.email)
    resp = await service.delete_ssh(uuid_)
    return resp

