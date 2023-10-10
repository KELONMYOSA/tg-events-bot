import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from src.tg_bot.models.checkbox_keyboard import CheckboxKeyboard
from src.tg_bot.models.dictionaries import topic2domain, topic2name
from src.tg_bot.models.user import User
from src.tg_bot.utils.dao import PostgreDB
from src.tg_bot.utils.settings import notification_interval_keyboard, n_button2interval, n_button2text, \
    domain_selection_keyboard, provider_selection_keyboard


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(commands=["settings"])
    async def settings(message: Message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="settings")

        await bot.delete_message(message.chat.id, message.message_id)

        settings_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Уведомления 🔔", callback_data="SettingsNotification"),
            InlineKeyboardButton("Тематики 🗂", callback_data="SettingsDomain"),
            InlineKeyboardButton("Источники мероприятий 📚", callback_data="SettingsProvider"),
            InlineKeyboardButton("Отмена", callback_data="SettingsCancel"),
            row_width=1
        )

        await bot.send_message(
            message.chat.id,
            "Настройки:",
            reply_markup=settings_keyboard
        )

        # user_logger.info(f"settings command", extra=user.build_extra())

    @bot.callback_query_handler(func=lambda call: call.data == "SettingsNotification")
    async def settings_notifications(call: CallbackQuery):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            "Выберите, как часто получать уведомления о мероприятиях:",
            reply_markup=notification_interval_keyboard("SettingsNotification")
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("SettingsNotification|"))
    async def settings_notifications_ok(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        n_button = int(call.data.split("|")[1])

        with PostgreDB() as db:
            db.set_push_interval(call.from_user.id, n_button2interval[n_button])

        await bot.send_message(
            call.message.chat.id,
            n_button2text[n_button]
        )

    @bot.callback_query_handler(func=lambda call: call.data == "SettingsDomain")
    async def settings_domain(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        await bot.send_message(
            call.message.chat.id,
            "Выберите тематики, которые Вам интересны:",
            reply_markup=domain_selection_keyboard(call.from_user.id, "SettingsDomain")
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("SettingsDomain|select|"))
    async def settings_domain_selection(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        keyboard = call.message.reply_markup
        keyboard = CheckboxKeyboard.change_button_selection(keyboard, call.data)

        await bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: "SettingsDomain|ok" == call.data)
    async def settings_domain_ok(call: CallbackQuery):
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

    @bot.callback_query_handler(func=lambda call: call.data == "SettingsProvider")
    async def settings_provider(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        await bot.send_message(
            call.message.chat.id,
            "Выберите тематики, которые Вам интересны:",
            reply_markup=provider_selection_keyboard(call.from_user.id, "SettingsDomain")
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("SettingsProvider|select|"))
    async def settings_provider_selection(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        keyboard = call.message.reply_markup
        keyboard = CheckboxKeyboard.change_button_selection(keyboard, call.data)

        await bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: "SettingsProvider|ok" == call.data)
    async def settings_provider_ok(call: CallbackQuery):
        msg_keyboard = call.message.reply_markup
        selected_texts = CheckboxKeyboard.get_selected_buttons(msg_keyboard)

        if len(selected_texts) == 0:
            await bot.answer_callback_query(
                call.id,
                "Источники не выбраны",
                show_alert=True
            )
        else:
            with PostgreDB() as db:
                providers = db.get_providers()
            provider_name2id = {}
            for provider in providers:
                provider_name2id[provider.name] = provider.id

            p_ids = []
            for text in selected_texts:
                p_ids.append(provider_name2id[text])

            with PostgreDB() as db:
                db.set_user_providers(call.from_user.id, p_ids)

            await bot.answer_callback_query(call.id, "Источники сохранены")
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(
                call.message.chat.id,
                "Источники сохранены"
            )

    @bot.callback_query_handler(func=lambda call: call.data == "SettingsCancel")
    async def settings_cancel(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
