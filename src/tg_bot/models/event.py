import datetime

from src.tg_bot.models.dictionaries import days_map, month_map


class Event:
    def __init__(self, id: int, original_text: str, title: str, date: datetime.datetime, date_add: datetime.datetime,
                 m_id: int = None, p_id: int = None, long_desc: str = None, short_desc: str = None,
                 time_b: datetime.datetime = None, time_e: datetime.datetime = None, place: str = None,
                 geo_id: int = None, url: str = None, is_online: bool = None, active: bool = None):
        self.id = id
        self.m_id = m_id
        self.p_id = p_id
        self.original_text = original_text
        self.title = title
        self.long_desc = long_desc
        self.short_desc = short_desc
        self.date = date
        self.time_b = time_b
        self.time_e = time_e
        self.place = place
        self.geo_id = geo_id
        self.url = url
        self.is_online = is_online
        self.date_add = date_add
        self.active = active

    def get_date_string(self) -> str:
        if self.time_b is None:
            date = self.date
        else:
            date = self.time_b
        now_day_number = date.weekday()
        short_str_day = days_map[now_day_number]
        month = month_map[date.month]
        day = date.day
        hour = date.hour
        minute = date.minute

        today = datetime.date.today()
        if today.day == date.day and \
                today.month == date.month and \
                today.year == date.year:
            if hour == 0:
                return f"Сегодня"
            else:
                return f"Сегодня в {hour:02d}:{minute:02d}"

        if (today + datetime.timedelta(1)).day == date.day and \
                (today + datetime.timedelta(1)).month == date.month and \
                (today + datetime.timedelta(1)).year == date.year:
            if hour == 0:
                return f"Завтра"
            else:
                return f"Завтра в {hour:02d}:{minute:02d}"

        if hour == 0:
            return f"{day} {month} ({short_str_day})"
        else:
            return f"{day} {month} ({short_str_day}) в {hour:02d}:{minute:02d}"
