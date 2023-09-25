from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship

from src.database import Base


class Song(Base):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True, index=True)
    file_link = Column(String, unique=True, index=True)
    file_size = Column(Float, nullable=True)
    title = Column(String, index=True)
    duration = Column(Float, index=True, nullable=True)
    created_at = Column(Date, default=datetime.utcnow(), index=True)

    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=True, index=True)
    artist = relationship('Artist', back_populates='songs')

    lyrics = relationship('Lyric', back_populates='song')


class Artist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    songs = relationship('Song', back_populates='artist')


class Lyric(Base):
    __tablename__ = 'lyrics'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)

    song_id = Column(Integer, ForeignKey('songs.id'))
    song = relationship('Song', back_populates='lyrics')
