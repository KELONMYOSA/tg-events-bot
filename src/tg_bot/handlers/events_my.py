from telebot.types import Message, CallbackQuery

from src.tg_bot.models.event_message import EventMessage
from src.tg_bot.models.pagination_keyboard import PaginationKeyboard
from src.tg_bot.utils.dao import PostgreDB


def run(bot):
    @bot.message_handler(commands=["my"])
    async def get_my_topic(message: Message):
        with PostgreDB() as db:
            domains = db.get_user_domains(message.from_user.id)
            event_ids = db.get_event_ids_by_domain_names(domains)
            events = db.get_events_by_ids(event_ids)

        pre_speech = "Моя подборка:"

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
                reply_markup=event_message.create_keyboard(f"EventsMy")
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("EventsMy"))
    async def events_my_pagination(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        with PostgreDB() as db:
            domains = db.get_user_domains(call.from_user.id)
            event_ids = db.get_event_ids_by_domain_names(domains)
            events = db.get_events_by_ids(event_ids)

        pre_speech = "Моя подборка:"

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
