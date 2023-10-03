def run(bot):
    @bot.message_handler(commands=["start"])
    async def start_bot(message):
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            """
Приветствую!

С этого момента все мероприятия с тобой в удобном формате.

Мероприятия по тематикам:
🖼 Выставки - /expo
🎉 Вечеринки - /party
🤡 StandUp - /standup
            """
        )
