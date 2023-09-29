from typing import Any, Dict, Optional
from datetime import timedelta, datetime
from pydantic import EmailStr, UUID4

from src.security import get_password_hash, verify_password, create_refresh_token, create_access_token
from src.crud.base import CRUDBase
from src.account.models import Account, Token
from src.account.schemas import UserCreate, UserUpdate, RefreshRequest
from src.database import AppSession
from uuid import uuid4

from sqlalchemy import select, insert, delete, update
from sqlalchemy.dialects.postgresql import insert as psql_insert
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
        user_data = obj_in.model_dump()
        password = user_data.pop('password')
        hashed_password = get_password_hash(password)
        user_data['hashed_password'] = hashed_password
        user_data['activation_code'] = uuid4()
        async with AppSession() as session:
            query = insert(Account).values(**user_data)
            await session.execute(query)
            await session.commit()
        return await self.get_by_email(email=user_data['email'])

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

    async def refresh_token(self, subject: int, exp: timedelta):
        async with AppSession() as session:
            token = create_refresh_token(subject=subject, expires_delta=exp)
            expires_at = datetime.utcnow() + exp
            query = psql_insert(
                Token
               ).values(
                    user_id=subject,
                    token=token,
                    exp_at=expires_at
                ).on_conflict_do_update(index_elements=['user_id'],
                                        set_=dict(exp_at=expires_at)).returning(Token)
            refresh_token = await session.execute(query)
            await session.commit()
            return refresh_token.scalars().one()

    async def refresh(self, refresh_data: dict):
        async with AppSession() as session:
            user_id: int = refresh_data['user_id']
            query = select(Token).where(Token.user_id == user_id)
            token_obj = await session.execute(query)
            token_obj = token_obj.scalars().one()
            token = token_obj.token
            if refresh_data['refresh_token'] != token:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail='Incorrect refresh_token')
            access_token = create_access_token(subject=user_id)
            return access_token

    @staticmethod
    def is_active(user_obj: Account) -> bool:
        return user_obj.is_active

    @staticmethod
    def is_superuser(user_obj: Account) -> bool:
        return user_obj.is_superuser

    async def make_admin(self, user_id: int):
        async with AppSession() as session:
            query = update(Account).where(Account.id == user_id).values(is_superuser=True).returning(Account)
            superuser = await session.execute(query)
            await session.commit()
            return superuser.scalars().one()


user = CRUDUser(Account)
