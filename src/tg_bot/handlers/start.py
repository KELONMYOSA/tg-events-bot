import logging

from telebot.types import Message, CallbackQuery

from src.tg_bot.models.checkbox_keyboard import CheckboxKeyboard
from src.tg_bot.models.dictionaries import topic2name, topic2domain
from src.tg_bot.models.user import User
from src.tg_bot.utils.dao import PostgreDB
from src.tg_bot.utils.settings import notification_interval_keyboard, n_button2interval, n_button2text, \
    domain_selection_keyboard


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(commands=["start"])
    async def start_bot(message: Message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="start")

        await bot.delete_message(message.chat.id, message.message_id)

        with PostgreDB() as db:
            db.set_user(message.from_user.id, message.from_user.username)

        await bot.send_message(
            message.chat.id,
            "Выберите тематики, которые Вам интересны:",
            reply_markup=domain_selection_keyboard(message.from_user.id, "StartUserDomains")
        )

        user_logger.info(f"new user", extra=user.build_extra())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("StartUserDomains|select|"))
    async def change_select_button(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        keyboard = call.message.reply_markup
        keyboard = CheckboxKeyboard.change_button_selection(keyboard, call.data)

        await bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: "StartUserDomains|ok" == call.data)
    async def set_domains_and_ask_notif(call: CallbackQuery):
        user = User(tg_id=call.from_user.id, tg_username=call.from_user.username, tg_action="start_domain")

        msg_keyboard = call.message.reply_markup
        selected_texts = CheckboxKeyboard.get_selected_buttons(msg_keyboard)

        if len(selected_texts) == 0:
            await bot.answer_callback_query(
                call.id,
                "Категории не выбраны",
                show_alert=True
            )
        else:
            domains = []
            for text in selected_texts:
                topic = list(filter(lambda x: topic2name[x] == text, topic2name))[0]
                domains.append(topic2domain[topic])

            with PostgreDB() as db:
                db.set_user_domains(call.from_user.id, domains)

            await bot.answer_callback_query(call.id, "Категории сохранены")
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(
                call.message.chat.id,
                "Категории сохранены"
            )

            await bot.send_message(
                call.message.chat.id,
                "Выберите, как часто получать уведомления о мероприятиях:",
                reply_markup=notification_interval_keyboard("StartNotification")
            )

            user_logger.info(f"new user configured domains", extra=user.build_extra())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("StartNotification|"))
    async def set_notifications_and_say_hello(call: CallbackQuery):
        user = User(tg_id=call.from_user.id, tg_username=call.from_user.username, tg_action="start_notification")

        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        n_button = int(call.data.split("|")[1])

        with PostgreDB() as db:
            db.set_push_interval(call.from_user.id, n_button2interval[n_button])

        await bot.send_message(
            call.message.chat.id,
            n_button2text[n_button]
        )

        await bot.send_message(
            call.message.chat.id,
            """
Готово! ✅

С этого момента все мероприятия ИТМО с тобой в удобном формате.

Мероприятия по тематикам:
🗂 Все темы - /all
❤️ Моя подборка - /my
🧠 Образование - /edu
💵 Бизнес, инновации - /money
📈 Карьера - /career
💃 Развлечения - /fun
⚽️ Спорт - /sport
👀 Остальное - /other

Ты всегда можешь изменить настройки - /settings
А также посмотреть список источников - /sources
            """
        )

        user_logger.info(f"new user configured notification schedule", extra=user.build_extra())
