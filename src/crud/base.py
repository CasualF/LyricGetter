from typing import Any, Dict, Generic, Optional, Type, TypeVar

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.database import AppSession
from sqlalchemy import select, insert, delete, update
from src.database import Base
from sqlalchemy.exc import CompileError

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: Any) -> Optional[ModelType]:
        async with AppSession() as session:
            query = select(self.model).filter_by(id=id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def get_list(self, **kwargs):
        async with AppSession() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)

        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> Any:
        if not isinstance(obj_in, dict):
            obj_data = {str(k): v for k,v in obj_in}
        obj_data = obj_in
        async with AppSession() as session:
            query = insert(self.model).values(**obj_data)
            await session.execute(query)
            await session.commit()
        return await self.get(id=obj_data['id'])

    async def update(self, pk: int | str, obj_in: UpdateSchemaType | Dict[str, Any]):
        async with AppSession() as session:
            obj_data = jsonable_encoder(obj_in)
            try:
                query = update(self.model).where(
                    self.model.email == pk).values(**obj_data).returning(self.model)
                result = await session.execute(query)
                await session.commit()
            except:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Missing arguments')
        return result.scalars().one()

    async def destroy(self, id: int) -> None:
        async with AppSession() as session:
            query = delete(self.model).filter_by(id=id)
            await session.execute(query)
            await session.commit()
