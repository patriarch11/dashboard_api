from fastapi import HTTPException, status

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
    )
UNIQUE_USER_EMAIL_EXCEPTION = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail='User with same email is already exists'
    )
INACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='user is inactive, for activate make login',
    )
INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate token from your auth provider',
    )
