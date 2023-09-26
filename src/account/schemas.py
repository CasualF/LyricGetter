from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    activation_code: Optional[UUID4] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None


class UserInDB(UserInDBBase):
    hashed_password: str


class User(UserInDBBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class UserResponse(BaseModel):
    msg: str
    data: User


class UsersListResponse(BaseModel):
    users: list[User]
