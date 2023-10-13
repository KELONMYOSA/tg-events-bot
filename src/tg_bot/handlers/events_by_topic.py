import logging

from telebot.types import CallbackQuery, Message

from src.tg_bot.models.dictionaries import topic2domain, topic2name
from src.tg_bot.models.event_message import EventMessage
from src.tg_bot.models.pagination_keyboard import PaginationKeyboard
from src.tg_bot.models.user import User
from src.tg_bot.utils.dao import PostgreDB


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(commands=["edu", "money", "career", "fun", "sport", "other"])
    async def get_events_by_topic(message: Message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="events_by_topic")

        topic = message.text[1:]

        domain = topic2domain[topic]
        pre_speech = f"{topic2name[topic]}:"

        with PostgreDB() as db:
            event_ids = db.get_event_ids_by_domain_names([domain])
            events = db.get_events_by_ids(event_ids)

        await bot.delete_message(message.chat.id, message.message_id)

        if not events:
            await bot.send_message(
                message.chat.id,
                "Мероприятия не найдены!"
            )
        else:
            event_message = EventMessage(events)
            await bot.send_message(
                message.chat.id,
                pre_speech + "\n\n" + event_message.get_message_text(0),
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=event_message.create_keyboard(f"EventsByTopic/{topic}")
            )

        user_logger.info(f"get events by topic", extra=user.build_extra())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("EventsByTopic"))
    async def events_by_topic_pagination(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        user = User(tg_id=call.from_user.id, tg_username=call.from_user.username,
                    tg_action="events_by_topic_pagination")

        topic = call.data.split("|")[0].split("/")[1]
        domain = topic2domain[topic]
        pre_speech = f"{topic2name[topic]}:"

        with PostgreDB() as db:
            event_ids = db.get_event_ids_by_domain_names([domain])
            events = db.get_events_by_ids(event_ids)

        event_message = EventMessage(events)
        page = PaginationKeyboard.get_current_page_from_callback(call.data)

        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            pre_speech + "\n\n" + event_message.get_message_text(page),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=event_message.change_keyboard_page(call.data)
        )

        user_logger.info(f"change events by topic page", extra=user.build_extra())
