from sqladmin import ModelView
from src.account.models import Account
from src.LyricGetter.models import Song


class UsersAdmin(ModelView, model=Account):
    column_list = [Account.id, Account.email,
                   Account.is_superuser, Account.is_active,
                   Account.first_name, Account.last_name]


class SongAdmin(ModelView, model=Song):
    column_list = [Song.title]


model_list = [UsersAdmin, SongAdmin]
