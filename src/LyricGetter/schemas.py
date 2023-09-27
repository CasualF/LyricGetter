from datetime import date

from src.account.models import Account
from src.LyricGetter.models import Artist, Lyric

from typing import Optional
from pydantic import BaseModel


class SongBase(BaseModel):
    file_link: str
    file_size: Optional[float]
    title: str
    cover: Optional[str]
    duration: Optional[float]
    created_at: Optional[date]
    artist_id: Optional[int]

    class Config:
        arbitrary_types_allowed = True


class SongInDB(SongBase):
    id: int


class ArtistSchema(BaseModel):
    nickname: str = None

    class Config:
        from_attributes = True


class ArtistInDB(ArtistSchema):
    id: int
    user_id: int
