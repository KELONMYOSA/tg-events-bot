import logging

from src.tg_bot.models.user import User


def run(bot):
    user_logger = logging.getLogger('user_stat')

    @bot.message_handler(func=lambda message: message.text not in ["/start", "/expo", "/party", "/standup", "/sources"])
    async def echo_all(message):
        user = User(tg_id=message.from_user.id, tg_username=message.from_user.username, tg_action="echo_all")

        await bot.delete_message(message.chat.id, message.message_id)

        user_logger.info(f"echo_all - message text: {message.text}", extra=user.build_extra())
