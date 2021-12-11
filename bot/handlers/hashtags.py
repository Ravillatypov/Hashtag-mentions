from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.base import dp, delete_message_after_callback, check_admin, is_admin
from db import Mentions, Hashtag


@dp.callback_query_handler(lambda cb: cb.data == 'get_hashtags')
async def get_hashtags(callback_query: CallbackQuery):
    hashtags = await Hashtag.filter(chat_id=callback_query.message.chat.id).all()
    await callback_query.answer('Пока хэштегов не добавлено' if not hashtags else None)

    if not hashtags:
        return

    markup = InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [InlineKeyboardButton(f'#{tag.hashtag}', callback_data=f'hashtag_{tag.id}')] for tag in hashtags
        ]
    )
    markup.add(InlineKeyboardButton('Хэштеги', callback_data='get_hashtags'))
    markup.add(InlineKeyboardButton('Подписки', callback_data='get_subscriptions'))
    await callback_query.message.edit_text('Список хэштегов')
    await callback_query.message.edit_reply_markup(markup)


@dp.callback_query_handler(lambda cb: cb.data.startswith('disable_hashtag_'))
@delete_message_after_callback
@check_admin
async def disable_hashtag(callback_query: CallbackQuery):
    await Hashtag.filter(
        id=callback_query.data.removeprefix('disable_hashtag_')
    ).update(is_enabled=False)
    await callback_query.answer('хэштег отключен')


@dp.callback_query_handler(lambda cb: cb.data.startswith('enable_hashtag_'))
@delete_message_after_callback
@check_admin
async def enable_hashtag(callback_query: CallbackQuery):
    await Hashtag.filter(
        id=callback_query.data.removeprefix('enable_hashtag_')
    ).update(is_enabled=True)
    await callback_query.answer('хэштег включен')


@dp.callback_query_handler(lambda cb: cb.data.startswith('delete_hashtag_'))
@delete_message_after_callback
@check_admin
async def delete_hashtag(callback_query: CallbackQuery):
    await Hashtag.filter(
        id=callback_query.data.removeprefix('delete_hashtag_')
    ).delete()
    await callback_query.answer('хэштег удален')


@dp.callback_query_handler(lambda cb: cb.data.startswith('hashtag_'))
async def hashtag_operations(callback_query: CallbackQuery):
    hashtag = await Hashtag.get(id=callback_query.data.removeprefix('hashtag_'))
    mention = await Mentions.get_or_none(hashtag=hashtag, user_id=callback_query.from_user.id)
    await callback_query.answer()

    hashtag_status = 'отключен, ' if not hashtag.is_enabled else ''
    mention_status = ''

    markup = InlineKeyboardMarkup(row_width=1)

    if mention and mention.is_enabled:
        mention_status = '(вы подписаны)'
        markup.add(InlineKeyboardButton('Отписаться', callback_data=f'unsubscribe_{mention.id}'))
        markup.add(InlineKeyboardButton('Отписаться на неделю', callback_data=f'week_unsubscribe_{mention.id}'))
        markup.add(InlineKeyboardButton('Отписаться на месяц', callback_data=f'month_unsubscribe_{mention.id}'))
        markup.add(InlineKeyboardButton('Отключить мою подписку', callback_data=f'disable_subscribe_{mention.id}'))

    if mention and not mention.is_enabled:
        mention_status = f'(отключено до {mention.enable_after})' if mention.enable_after else '(отключено)'
        markup.add(InlineKeyboardButton('Включить подписку', callback_data=f'subscribe_{hashtag.id}'))

    if not mention:
        mention_status = '(вы не подписаны)'
        markup.add(InlineKeyboardButton('Подписаться', callback_data=f'subscribe_{hashtag.id}'))

    if await is_admin(callback_query.message.chat, callback_query.from_user.id):
        if hashtag.is_enabled:
            markup.add(InlineKeyboardButton('Отключить хэштег', callback_data=f'disable_hashtag_{hashtag.id}'))
        else:
            markup.add(InlineKeyboardButton('Включить хэштег', callback_data=f'enable_hashtag_{hashtag.id}'))
        markup.add(InlineKeyboardButton('Удалить хэштег', callback_data=f'delete_hashtag_{hashtag.id}'))

    markup.add(InlineKeyboardButton('Закрыть', callback_data='cancel'))
    await callback_query.message.answer(
        f'@{callback_query.from_user.username} #{hashtag.hashtag} - {hashtag_status}{mention_status}',
        reply_markup=markup
    )


@dp.callback_query_handler(lambda cb: cb.data == 'cancel')
async def cancel(callback_query: CallbackQuery):
    await callback_query.message.delete()
