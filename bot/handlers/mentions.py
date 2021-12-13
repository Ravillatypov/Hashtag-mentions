from datetime import datetime, timedelta

from aiogram.types import MessageEntityType, ContentType, Message, CallbackQuery

from bot.base import dp, delete_message_after_callback, parse_hashtags
from db import Mentions, User
from itertools import groupby


@dp.callback_query_handler(lambda cb: cb.data.startswith('unsubscribe_'))
@delete_message_after_callback
async def unsubscribe(callback_query: CallbackQuery):
    await Mentions.filter(
        id=callback_query.data.removeprefix('unsubscribe_'),
    ).delete()
    await callback_query.answer(f'{callback_query.from_user.full_name}, вы отписаны')


@dp.callback_query_handler(lambda cb: cb.data.startswith('week_unsubscribe_'))
@delete_message_after_callback
async def week_unsubscribe(callback_query: CallbackQuery):
    after_week = datetime.utcnow() + timedelta(weeks=1)
    after_week = after_week.date()

    await Mentions.filter(
        id=callback_query.data.removeprefix('week_unsubscribe_'),
    ).update(enable_after=after_week, is_enabled=False)

    await callback_query.answer(f'{callback_query.from_user.full_name}, вы отписаны до {after_week}')


@dp.callback_query_handler(lambda cb: cb.data.startswith('month_unsubscribe_'))
@delete_message_after_callback
async def month_unsubscribe(callback_query: CallbackQuery):
    now = datetime.utcnow()
    next_month = now.replace(day=28) + timedelta(days=10)
    after_month = next_month.replace(day=now.day).date()

    await Mentions.filter(
        id=callback_query.data.removeprefix('month_unsubscribe_'),
    ).update(enable_after=after_month, is_enabled=False)

    await callback_query.answer(f'{callback_query.from_user.full_name}, вы отписаны до {after_month}')


@dp.callback_query_handler(lambda cb: cb.data.startswith('disable_subscribe_'))
@delete_message_after_callback
async def disable_subscribe(callback_query: CallbackQuery):
    await Mentions.filter(
        id=callback_query.data.removeprefix('disable_subscribe_'),
    ).update(enable_after=None, is_enabled=False)

    await callback_query.answer(f'{callback_query.from_user.full_name}, подписка отключена')


@dp.callback_query_handler(lambda cb: cb.data.startswith('subscribe_'))
@delete_message_after_callback
async def subscribe(callback_query: CallbackQuery):
    if not callback_query.from_user.username:
        return await callback_query.answer(
            'Нужно установить username в Telegram, чтобы я мог вас упомянуть',
            show_alert=True,
        )

    user, _ = await User.get_or_create(
        id=callback_query.from_user.id,
        defaults={
            'first_name': callback_query.from_user.first_name,
            'last_name': callback_query.from_user.last_name,
            'username': callback_query.from_user.username,
        }
    )

    mention, _ = await Mentions.get_or_create(
        hashtag_id=callback_query.data.removeprefix('subscribe_'),
        user_id=callback_query.from_user.id,
    )

    if not mention.is_enabled:
        mention.is_enabled = True
        mention.enable_after = None
        await mention.save()

    await callback_query.answer(f'{callback_query.from_user.full_name}, вы подписаны')


@dp.callback_query_handler(lambda cb: cb.data == 'get_subscriptions')
async def get_subscriptions(callback_query: CallbackQuery):
    hashtags = await Mentions.filter(
        is_enabled=True,
        hashtag__is_enabled=True,
        hashtag__chat_id=callback_query.message.chat.id,
    ).prefetch_related(
        'hashtag', 'user'
    ).order_by(
        'hashtag__created_at', 'created_at'
    ).values_list('hashtag__hashtag', 'user__first_name', 'user__last_name')

    await callback_query.answer('Пока нет подписок на хэштеги' if not hashtags else None)

    if not hashtags:
        return

    text = 'Активные подписки:\n'
    for tag, users in groupby(hashtags, key=lambda v: v[0]):
        user_names = ', '.join([f"{f} {l}" for _, f, l in users])
        text += f'#{tag}: {user_names}\n'

    await callback_query.message.reply(text)


@dp.message_handler(
    lambda msg: any([e.type == MessageEntityType.HASHTAG for e in msg.entities]),
    content_types=ContentType.TEXT
)
async def handle_hashtags(message: Message):
    if message.from_user.id == dp.bot.id:
        return

    hastags = parse_hashtags(message)

    usernames = await Mentions.filter(
        is_enabled=True,
        hashtag__hashtag__in=hastags,
        hashtag__is_enabled=True,
        hashtag__chat_id=message.chat.id,
        user_id__not=message.from_user.id,
    ).values_list('user__username', flat=True)

    if usernames:
        await message.answer(', '.join([f'@{u}' for u in usernames if u]))
