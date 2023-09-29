from sqlalchemy import Boolean, Column, Integer, String, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


class Account(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    activation_code = Column(UUID, nullable=True)

    artist = relationship('Artist', back_populates='user')
    token = relationship('Token', back_populates='user')

    def __str__(self):
        return self.email


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    exp_at = Column(DateTime, nullable=False)

    user = relationship('Account', back_populates='token')

    def __str__(self):
        return self.token
