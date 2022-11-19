import datetime
import hashlib
import os
import uuid
from io import BytesIO

import boto3
import rsa
from fastapi import (
    HTTPException,
    status,
    UploadFile
)
from ormar import NoMatch

from app import models
from app.config import settings

s3_resource = boto3.resource(
    service_name='s3',
    region_name=settings.aws_region_name,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)
s3_client = boto3.client(
    service_name='s3',
    region_name=settings.aws_region_name,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)


class SSHService:

    def __init__(self, owner_id: int, owner_name: str):
        self.owner_id = owner_id
        self.owner_name = owner_name

    async def create_ssh_pair(self, pair_name: str) -> models.SSHPair:

        await self.check_number_of_keys()

        uuid_ = uuid.uuid4()

        public_key, private_key = self.generate_ssh_pair()

        gen_date = datetime.datetime.now()

        public_name = f'{self.owner_name}/ssh/{uuid_}-public.pem'
        private_name = f'{self.owner_name}/ssh/{uuid_}-private.pem'

        fp_pub, fp_prvt = await self.get_fingerprint(public_key, private_key)

        self.upload_to_s3_ssh_pair(
            public_key, private_key,
            public_name, private_name
        )

        ssh_pair = await self.attach_to_db(
            gen_date, pair_name, uuid_,
            self.owner_name, fp_pub, fp_prvt
        )

        return ssh_pair

    async def add_ssh_pair(self, public_key_: UploadFile, private_key_: UploadFile, pair_name: str):
        await self.check_number_of_keys()

        uuid_ = uuid.uuid4()

        gen_date = datetime.datetime.now()

        public_key, private_key = public_key_.file, private_key_.file
        public_name = f'{self.owner_name}/ssh/{uuid_}-public.pem'
        private_name = f'{self.owner_name}/ssh/{uuid_}-private.pem'
        self.upload_to_s3_ssh_pair(
            public_key.read(), private_key.read(),
            public_name, private_name
        )
        # self.check_key_pair(public_key_, private_key_)
        fp_pub, fp_prvt = await self.get_fingerprint(public_key.read(), private_key.read())
        # print(public_key.read(), private_key.read())
        ssh_pair = await self.attach_to_db(
            gen_date, pair_name, uuid_,
            self.owner_name, fp_pub, fp_prvt
        )

        return ssh_pair

    async def get_my_keys_info(self) -> list[models.SSHPair]:
        return await models.SSHPair.objects.filter(owner_id=self.owner_id).all()

    async def download_ssh_key(self, uuid_: uuid.UUID, type_: str) -> tuple[bytes, str]:

        pair_info = await self.get_pair_info(uuid_)

        key_s3_uri = f'{pair_info.owner_name}/ssh/{pair_info.uuid_}-{type_}.pem'
        name = f'{pair_info.uuid_}-{type_}.pem'

        with open(name, 'wb') as f:
            s3_resource.Bucket(settings.s3_bucket_name).download_fileobj(
                key_s3_uri,
                f
            )

        with open(name, 'rb') as f:
            file_bytes = f.read()

        os.remove(name)

        return file_bytes, name

    async def delete_ssh(self, uuid_: uuid.UUID):

        pair_info = await self.get_pair_info(uuid_)

        await models.SSHPair.objects.delete(
            owner_id=self.owner_id,
            uuid_=pair_info.uuid_
        )

        response_pub = s3_client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=f'{pair_info.owner_name}/ssh/{pair_info.uuid_}-public.pem'
        )
        response_prv = s3_client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=f'{pair_info.owner_name}/ssh/{pair_info.uuid_}-private.pem'
        )
        return response_pub, response_prv

    async def get_pair_info(self, uuid_: uuid.UUID) -> models.SSHPair:
        try:
            pair_info: models.SSHPair = await models.SSHPair.objects.filter(
                owner_id=self.owner_id,
                uuid_=uuid_
            ).first()
        except NoMatch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"msg": "you don't have this key pair"}
            )
        return pair_info

    async def attach_to_db(
            self,
            gen_date: datetime.datetime,
            pair_name: str,
            uuid_: uuid.UUID,
            owner_name: str,
            fp_pub: str,
            fp_prvt: str
    ) -> models.SSHPair:
        ssh_pair = await models.SSHPair.objects.create(
            owner_id=self.owner_id,
            gen_date=gen_date,
            pair_name=pair_name,
            uuid_=uuid_,
            owner_name=owner_name,
            fp_pub=fp_pub,
            fp_prvt=fp_prvt
        )
        return ssh_pair

    async def check_number_of_keys(self) -> None:
        keys = await models.SSHPair.objects.filter(owner_id=self.owner_id).all()

        if len(keys) >= settings.max_number_ssh_keys:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"msg": "an excess is permissible for the number of keys"}
            )

    @staticmethod
    async def get_fingerprint(pub_key: bytes, prvt_key: bytes) -> tuple[str, str]:

        fp_plain_pub = hashlib.md5(pub_key).hexdigest()
        fp_plain_prvt = hashlib.md5(prvt_key).hexdigest()
        fp_pub = ':'.join(a + b for a, b in zip(fp_plain_pub[::2], fp_plain_pub[1::2]))
        fp_prvt = ':'.join(a + b for a, b in zip(fp_plain_prvt[::2], fp_plain_prvt[1::2]))
        return fp_pub, fp_prvt

    @staticmethod
    def generate_ssh_pair() -> tuple[bytes, bytes]:
        public_key, private_key = rsa.newkeys(settings.ssh_key_size)
        return public_key.save_pkcs1("PEM"), private_key.save_pkcs1("PEM")

    @staticmethod
    def upload_to_s3_ssh_pair(
            public_key_file: bytes,
            private_key_file: bytes,
            public_file_name: str,
            private_file_name: str,
    ) -> None:
        s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(
            BytesIO(public_key_file),
            public_file_name
        )
        s3_resource.Bucket(settings.s3_bucket_name).upload_fileobj(
            BytesIO(private_key_file),
            private_file_name
        )

    # @staticmethod
    # def check_key_pair(public_key: UploadFile, private_key: UploadFile):
    #
    #     if public_key.filename.strip().split('.')[1] != 'pem':
    #         raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    #
    #     if private_key.filename.strip().split('.')[1] != 'pem':
    #         raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    #
    #     # if '-----BEGIN RSA PUBLIC KEY-----' in public_key.file.read().decode():
    #     #     pass
    #     # else:
    #     #     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    #     #
    #     # if '-----BEGIN RSA PRIVATE KEY-----' in private_key.file.read().decode():
    #     #     pass
    #     # else:
    #     #     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    #
    #     print(public_key.file.read())
