from jose import jwt
from pydantic import ValidationError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.account.models import Account
from src.account.schemas import TokenPayload
from src.config import settings
from src import crud

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"api/users/login/"
)


async def get_current_user(token: str = Depends(reusable_oauth2)) -> Account:
    try:
        payload = jwt.decode(
            token, settings.SECRET, algorithms=[settings.HASHING_ALGORYTHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
    return user


async def get_current_superuser(current_user: Account = Depends(get_current_user)) -> Account:
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user
