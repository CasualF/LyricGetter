from sqladmin import ModelView
from src.account.models import Account
from src.LyricGetter.models import Song, Artist


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
    column_list = [Song.title, Song.artist]
    icon = 'fa-solid fa-music'


model_list = [UsersAdmin, SongAdmin]
