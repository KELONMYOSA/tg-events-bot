import datetime
import logging
import time

import pytz as pytz
import schedule as schedule
from telebot import TeleBot

from src.config.config import settings
from src.tg_bot.models.dictionaries import topic2domain
from src.tg_bot.models.event_message import EventMessage
from src.tg_bot.utils.dao import PostgreDB

bot = TeleBot(settings.BOT_TOKEN)
logger = logging.getLogger('default')


def push_events():
    with PostgreDB() as db:
        notif_data = db.get_notification_data()

    for row in notif_data:
        user_id, interval, next_push_date = row

        if interval != 0 and next_push_date.date() <= datetime.date.today():
            try:
                with PostgreDB() as db:
                    domains = db.get_user_domains(user_id)
                    if not domains:
                        domains = list(topic2domain.values())
                    event_ids_d = db.get_event_ids_by_domain_names(domains)

                    provider_ids = db.get_user_providers(user_id)
                    if not provider_ids:
                        provider_ids = [provider.id for provider in db.get_providers()]
                    event_ids_p = db.get_event_ids_by_provider_ids(provider_ids)

                    event_ids = list(set(event_ids_d) & set(event_ids_p))
                    events = db.get_events_by_ids(event_ids)

                pre_speech = "Персональная подборка мероприятий:"

                if events:
                    event_message = EventMessage(events)
                    bot.send_message(
                        user_id,
                        pre_speech + "\n\n" + event_message.get_message_text(0),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=event_message.create_keyboard(f"EventsMy")
                    )

                with PostgreDB() as db:
                    db.set_next_push_date(user_id, datetime.datetime.now() + datetime.timedelta(interval))

                logger.info("Push - Message send to user", extra={"tags": {"tg_id": user_id}})

            except Exception as exp:
                logger.error("Unable to send a message to user", exc_info=exp,
                             extra={"tags": {"tg_id": user_id}})


def schedule_push_events():
    schedule.every().day.at(time_str="11:00", tz=pytz.timezone("Europe/Moscow")).do(push_events)

    while True:
        schedule.run_pending()
        time.sleep(1)
