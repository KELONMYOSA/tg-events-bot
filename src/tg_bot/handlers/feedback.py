import logging

from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.config.config import settings
from src.tg_bot.models.user import User


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(commands=["feedback"])
    async def feedback(message: Message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="feedback")

        button = InlineKeyboardButton("Google Forms", url=settings.FEEDBACK_LINK)
        markup = InlineKeyboardMarkup().add(button)

        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            "Предложения и обратная связь:",
            reply_markup=markup
        )

        user_logger.info(f"get feedback form link", extra=user.build_extra())
