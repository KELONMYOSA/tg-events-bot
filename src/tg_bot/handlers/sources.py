from src.tg_bot.utils.dao import PostgreDB


def run(bot):
    @bot.message_handler(commands=["sources"])
    async def sources(message):
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
