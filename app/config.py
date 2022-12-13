from pydantic import BaseSettings

from dotenv import (
    load_dotenv,
    find_dotenv
)

import os

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    # app settings
    server_host: str = "http://localhost"
    server_port: int = 8000
    # db settings
    db_url: str = f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}" \
                  f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"

    # cors settings
    frontend_url: str
    backend_url: str

    # JWT settings
    jwt_secret: str
    jwt_algorithm: str
    jwt_exp: int = 60

    # google open_id settings
    google_client_id: str
    google_client_secret: str
    google_discovery_url: str = "https://accounts.google.com/.well-known/openid-configuration"

    # azure open_id settings
    azure_client_id: str
    azure_tenant_id: str

    # google smtp settings
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int
    mail_from_name: str
    mail_subject_line: str
    mail_tls: bool = True
    mail_ssl: bool = False
    use_credentials: bool = True
    validate_credentials: bool = True

    # ssh keys settings
    ssh_key_size: int = 128
    max_number_ssh_keys: int = 100

    # aws storage settings
    s3_bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region_name: str


settings = Settings(
    _env_file="../.env",
    _env_file_encoding="utf-8"
)
