import importlib
import pkgutil
import asyncio

from telebot.async_telebot import AsyncTeleBot

from src.config.config import settings
from src.tg_bot import handlers

bot = AsyncTeleBot(settings.BOT_TOKEN)

try:
    for x in pkgutil.iter_modules(handlers.__path__):
        handler = importlib.import_module("src.tg_bot.handlers." + x.name)
        handler.run(bot)
except Exception as e:
    print(f"Error occurred: {e}")

print("bot started >>> GO,GO,GO!")

asyncio.run(bot.polling())
