from typing import Optional, Any

from src.crud.base import CRUDBase
from src.LyricGetter.models import Song, Artist
from src.LyricGetter.schemas import SongBase, ArtistSchema
from src.database import AppSession

from sqlalchemy import insert, select, or_
from fastapi import HTTPException, status


class CRUDSong(CRUDBase[Song, SongBase, SongBase]):
    async def get_by_title(self, title: str) -> Optional[Song]:
        async with AppSession() as session:
            query = select(Song).filter_by(title=title)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def create(self, obj_in: SongBase) -> Any:
        if not isinstance(obj_in, dict):
            obj_data = {str(k): v for k,v in obj_in}
        obj_data = obj_in
        async with AppSession() as session:
            query = insert(Song).values(**obj_data)
            await session.execute(query)
            await session.commit()
        return await self.get_by_title(title=obj_data['title'])

    async def search_song(self, param: str):
        async with AppSession() as session:
            query = select(Song).join(Artist, isouter=True).where(
                or_(
                    Song.title.icontains(param),
                    Artist.nickname.icontains(param)
                )
            )
            songs = await session.execute(query)
            return songs.scalars()

    async def create_artist(self, user_data):
        async with AppSession() as session:
            get_artist_query = select(Artist).where(Artist.user_id == user_data['user_id'])
            artist = await session.execute(get_artist_query)
            if artist.one_or_none():
                raise HTTPException(detail='You are already an artist',
                                    status_code=status.HTTP_409_CONFLICT)
            query = insert(Artist).values(**user_data).returning(Artist)
            artist = await session.execute(query)
            await session.commit()
            return artist.scalar()


song = CRUDSong(Song)
