from typing import Any, Dict, Optional
from pydantic import EmailStr, UUID4

from src.security import get_password_hash, verify_password
from src.crud.base import CRUDBase
from src.account.models import Account
from src.account.schemas import UserCreate, UserUpdate
from src.database import AppSession
from uuid import uuid4

from sqlalchemy import select, insert, delete, update
from fastapi import HTTPException, status


class CRUDUser(CRUDBase[Account, UserCreate, UserUpdate]):
    @staticmethod
    async def get_by_email(email: str) -> Optional[Account]:
        async with AppSession() as session:
            query = select(Account).filter_by(email=email)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    @staticmethod
    async def activate_user(code: UUID4) -> Any:
        async with AppSession() as session:
            try:
                query = update(Account).where(Account.activation_code == code
                                              ).values(is_active=True,
                                                       activation_code=None).returning(Account)
                result = await session.execute(query)
                print(result.scalars().one())
                await session.commit()
            except Exception as e:
                print(e)
                raise HTTPException(detail='User not found',
                                    status_code=status.HTTP_404_NOT_FOUND)

    async def create(self, obj_in: UserCreate) -> Any:
        db_obj = obj_in.model_dump()
        password = db_obj.pop('password')
        hashed_password = get_password_hash(password)
        db_obj['hashed_password'] = hashed_password
        db_obj['activation_code'] = uuid4()
        async with AppSession() as session:
            query = insert(Account).values(**db_obj)
            await session.execute(query)
            await session.commit()
        return await self.get_by_email(email=db_obj['email'])

    async def update(self, email: EmailStr, obj_in: UserUpdate | Dict[str, Any]) -> Account:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump()
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(pk=email, obj_in=update_data)

    async def destroy(self, email: EmailStr) -> None:
        async with AppSession() as session:
            query = delete(Account).filter_by(email=email)
            await session.execute(query)
            await session.commit()

    async def authenticate(self, email: str, password: str) -> Optional[Account]:
        user_obj = await self.get_by_email(email=email)
        if not user_obj:
            return None
        if not verify_password(password, user_obj.hashed_password):
            return None
        return user_obj

    @staticmethod
    def is_active(user_obj: Account) -> bool:
        return user_obj.is_active

    @staticmethod
    def is_superuser(user_obj: Account) -> bool:
        return user_obj.is_superuser


user = CRUDUser(Account)
