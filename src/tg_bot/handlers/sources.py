import logging

from telebot.types import Message

from src.tg_bot.utils.dao import PostgreDB
from src.tg_bot.models.user import User


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(commands=["sources"])
    async def sources(message: Message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="sources")

        with PostgreDB() as db:
            providers = db.get_providers()
        sources_text = "Список источников:\n"
        for provider in providers:
            sources_text += f"\n-️ <a href='{provider.url}'>{provider.name}</a>"

        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            sources_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

        user_logger.info(f"sources", extra=user.build_extra())
