from sqladmin import ModelView
from src.account.models import Account, Token
from src.LyricGetter.models import Song, Artist, Lyric


class UsersAdmin(ModelView, model=Account):
    column_list = ['id', 'email',
                   'is_superuser', 'is_active',
                   'first_name', 'last_name']
    can_delete = False
    name = 'User'
    name_plural = 'Users'
    icon = 'fa-solid fa-user'
    column_details_exclude_list = ['hashed_password']


class SongAdmin(ModelView, model=Song):
    column_list = ['id', 'title', 'artist']
    icon = 'fa-solid fa-music'


class ArtistAdmin(ModelView, model=Artist):
    column_list = ['id', 'nickname']
    icon = 'fa-solid fa-microphone'


class LyricAdmin(ModelView, model=Lyric):
    icon = 'fa-solid fa-closed-captioning'


class TokenAdmin(ModelView, model=Token):
    column_list = ['token', 'user']
    icon = 'fa-solid fa-key'
    can_delete = False
    can_edit = False


model_list = [UsersAdmin, SongAdmin, ArtistAdmin,
              LyricAdmin, TokenAdmin]
