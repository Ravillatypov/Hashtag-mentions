from os import environ

from tortoise import Model, Tortoise
from tortoise.fields import (
    UUIDField, CharField, BigIntField, ForeignKeyField, ForeignKeyRelation, BooleanField, DateField, DatetimeField
)

__all__ = ['init_db', 'Chat', 'User', 'Mentions', 'Hashtag']


async def init_db(db_url: str = None):
    if not db_url:
        db_url = environ.get('DB_URL', default='sqlite://db.sqlite3')

    await Tortoise.init(db_url=db_url, modules={'models': ['db']}, use_tz=True)
    await Tortoise.generate_schemas()


class Chat(Model):
    id = BigIntField(pk=True, generated=False)
    name = CharField(max_length=255)


class User(Model):
    id = BigIntField(pk=True, generated=False)
    updated_at = DatetimeField(auto_now=True)
    first_name = CharField(max_length=255, null=False)
    last_name = CharField(max_length=255, null=False)
    username = CharField(max_length=255, null=False)


class Hashtag(Model):
    id = UUIDField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    hashtag = CharField(max_length=255)
    is_enabled = BooleanField(default=True)
    is_case_sensitive = BooleanField(default=False)
    chat: ForeignKeyRelation[Chat] = ForeignKeyField('models.Chat', related_name='tags')


class Mentions(Model):
    id = UUIDField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    is_enabled = BooleanField(default=True)
    enable_after = DateField(null=True)
    user: ForeignKeyRelation[User] = ForeignKeyField('models.User', related_name='mentions')
    hashtag: ForeignKeyRelation[Hashtag] = ForeignKeyField('models.Hashtag', related_name='mentions')
