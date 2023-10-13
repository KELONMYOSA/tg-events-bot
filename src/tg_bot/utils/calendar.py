import datetime
from urllib.parse import urlencode

from src.tg_bot.models.event import Event


def make_google_cal_url(event: Event) -> str:
    url = "https://www.google.com/calendar/render?action=TEMPLATE&"
    event_end_date = (event.date - datetime.timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    event_date = (event.date - datetime.timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")
    params = {"text": event.title, "details": event.short_desc + "\n\n" + event.url,
              "location": event.place, "dates": event_date + "/" + event_end_date}

    return url + urlencode(params)
