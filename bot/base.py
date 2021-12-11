from os import environ
from typing import List, Callable, Awaitable, Union

from aiocache import cached
from aiogram import Dispatcher, Bot
from aiogram.types import MessageEntityType, Message, CallbackQuery, Chat

bot = Bot(token=environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher(bot)

HandlerType = Callable[[Union[CallbackQuery, Message]], Awaitable]


@cached(ttl=300, key_builder=lambda _, chat, user_id: f'is_admin_{chat.id}_{user_id}')
async def is_admin(chat: Chat, user_id: int) -> bool:
    """
    check the user`s permissions in the current chat
    :param chat:
    :param user_id:
    :return:
    """
    member = await chat.get_member(user_id)
    return member.is_chat_owner or member.is_chat_admin()


def check_admin(func: HandlerType) -> HandlerType:
    """
    decorator to check the user`s permission before calling a function
    :param func:
    :return:
    """
    async def wrapper(msg):
        if isinstance(msg, CallbackQuery):
            chat = msg.message.chat
            user_id = msg.message.from_user.id
        else:
            chat = msg.chat
            user_id = msg.from_user.id

        if await is_admin(chat, user_id):
            return await func(msg)

    return wrapper


def delete_message_after_callback(func: HandlerType) -> HandlerType:
    """
    decorator for deleting callback messages after calling a function
    :param func:
    :return:
    """
    async def wrapper(cb: CallbackQuery):
        await func(cb)
        await cb.message.delete()
    return wrapper


def parse_hashtags(message: Message) -> List[str]:
    """
    parse hashtags from message
    :param message:
    :return:
    """
    return [
        message.text[e.offset + 1:e.offset + e.length] for e in message.entities if e.type == MessageEntityType.HASHTAG
    ]
