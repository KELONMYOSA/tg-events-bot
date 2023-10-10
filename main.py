import importlib
import logging
import pkgutil
import asyncio

from logging.config import dictConfig

from telebot.async_telebot import AsyncTeleBot

from src.config.config import settings
from src.config.log_config import LOG_CONFIG
from src.tg_bot import handlers

dictConfig(LOG_CONFIG)
logger = logging.getLogger('default')
loki_handler = next((x for x in logger.handlers if x.name == "loki"), None)
logging.getLogger("TeleBot").addHandler(loki_handler)

bot = AsyncTeleBot(settings.BOT_TOKEN)

try:
    for x in pkgutil.iter_modules(handlers.__path__):
        handler = importlib.import_module("src.tg_bot.handlers." + x.name)
        handler.run(bot)

    logger.info("ITMO Events TG Bot Started")
    asyncio.run(bot.polling())
except Exception as e:
    logger.critical("Failed to import handlers", exc_info=e)
