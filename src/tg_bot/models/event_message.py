from telebot.types import InlineKeyboardMarkup

from src.tg_bot.models.event import Event
from src.tg_bot.models.pagination_keyboard import PaginationKeyboard


class EventMessage:
    def __init__(self, events: list[Event] | Event, is_digest: bool = True, events_on_page: int = 5):
        self._events = events if type(events) is list else [events]
        self._events_on_page = events_on_page
        self._event_pages = self.__splitting_events_into_pages(self._events, self._events_on_page)
        self._keyboard = None
        self.is_digest = is_digest

    @staticmethod
    def __splitting_events_into_pages(events: list[Event], events_on_page: int) -> list[list[Event]]:
        return [events[i:i + events_on_page] for i in range(0, len(events), events_on_page)]

    @staticmethod
    def __get_digest_message_text(events: list[Event]) -> str:
        message_text = ""
        for event in events:
            place_text = ('\n📍 ' + event.place) if event.place else ''
            message_text += \
                f"\n\n🦄️ <a href='{event.url}'>{event.title}</a>" \
                f"\n🗓 {event.get_date_string()}" \
                f"{place_text}" \
                f"\n{event.short_desc}"

        message_text = message_text[2:]

        return message_text

    @staticmethod
    def __get_detailed_message_text(events: list[Event]) -> str:
        message_text = ""
        for event in events:
            message_text += \
                f"\n\n🦄️ <a href='{event.url}'>{event.title}</a>" \
                f"\n🗓 {event.get_date_string()}" \
                f"\n📍 {event.place}" \
                f"\n{event.long_desc}"

        message_text = message_text[2:]

        return message_text

    def __page_count(self) -> int:
        return len(self._event_pages)

    def get_message_text(self, page: int) -> str:
        if page > self.__page_count() - 1 or page < -self.__page_count():
            return "Мероприятия не найдены!"
        if self.is_digest:
            return self.__get_digest_message_text(self._event_pages[page])
        else:
            return self.__get_detailed_message_text(self._event_pages[page])

    def create_keyboard(self, callback_name: str) -> InlineKeyboardMarkup:
        self._keyboard = PaginationKeyboard(callback_name, self.__page_count())
        return self._keyboard.create_keyboard()

    def change_keyboard_page(self, callback_text: str) -> InlineKeyboardMarkup:
        if self._keyboard is None:
            callback_name = PaginationKeyboard.get_call_name_from_callback(callback_text)
            self._keyboard = PaginationKeyboard(callback_name, self.__page_count())

        return self._keyboard.change_page(callback_text)
