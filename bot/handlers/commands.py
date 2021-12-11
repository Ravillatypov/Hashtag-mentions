from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.base import dp, parse_hashtags, is_admin
from db import Chat, Hashtag


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    send the help message and menu
    :param message:
    :return:
    """
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton('Хэштеги', callback_data='get_hashtags')],
            [InlineKeyboardButton('Подписки', callback_data='get_subscriptions')],
        ],
        row_width=1,
    )
    _, is_created = await Chat.get_or_create(
        id=message.chat.id,
        defaults={'name': message.chat.username or message.chat.title or ''}
    )

    if is_created or message.get_command(True) == 'help':
        await message.answer('''Помогу упомянуть всех заинтересованных участников группы по хэштегу. \
        Участники сами могут управлять подписками на хэштегов. Например отписаться на месяц, пока в отпуске.

Как пользоваться:
1. Создай хэштег, например: /create_hashtag #mytag, #other text message ... #lasttag
2. Сами участники смогут подписаться на нужные хэштеги
3. Во всех сообщениях где встречается хэштег, буду упомянуты подписанные пользователи
 ''', reply_markup=markup)
    else:
        await message.answer('Что хотите сделать?', reply_markup=markup)


@dp.message_handler(commands=['create_hashtag'])
async def create_tags(message: Message):
    """
    create tags handler
    :param message:
    :return:
    """
    hashtags = parse_hashtags(message)

    if not hashtags:
        await message.answer('Увы, не смог найти тут хэштегов. Может забыли поставить #?')

    elif await is_admin(message.chat, message.from_user.id):
        chat, _ = await Chat.get_or_create(
            id=message.chat.id,
            defaults={'name': message.chat.username or message.chat.title or ''}
        )

        exists = await Hashtag.filter(
            hashtag__in=hashtags,
            chat=chat,
        ).values_list('hashtag', flat=True)

        to_create = [Hashtag(chat=chat, hashtag=h) for h in hashtags if h not in exists]

        if to_create:
            await Hashtag.bulk_create(to_create)
            created = ', '.join([t.hashtag for t in to_create if t.id])
            await message.answer(f'Добавлены: {created}')
        else:
            await message.answer('Уже добавлены')

    else:
        await message.answer('Эта команда только для администраторов группы')
