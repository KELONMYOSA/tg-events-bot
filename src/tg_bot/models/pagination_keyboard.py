from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class PaginationKeyboard:
    def __init__(self, callback_name: str, n_pages: int):
        self._callback_name = callback_name
        self._n_pages = n_pages

    def create_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        if self._n_pages > 1:
            next_page_button = InlineKeyboardButton("Далее", callback_data=f"{self._callback_name}|next|0")
            keyboard.add(next_page_button)

        return keyboard

    @staticmethod
    def get_current_page_from_callback(callback_text: str) -> int:
        callback_data = callback_text.split("|")
        if callback_data[1] == "next":
            return int(callback_text.split("|")[2]) + 1
        else:
            return int(callback_text.split("|")[2]) - 1

    @staticmethod
    def get_call_name_from_callback(callback_text: str) -> str:
        return callback_text.split("|")[0]

    def change_page(self, callback_text: str) -> InlineKeyboardMarkup:
        callback_data = callback_text.split("|")
        callback_name = callback_data[0]
        command = callback_data[1]
        cur_page = int(callback_data[2])
        keyboard = InlineKeyboardMarkup()

        if command == "next":
            if cur_page < self._n_pages - 2:
                next_page_button = InlineKeyboardButton("Далее", callback_data=f"{callback_name}|next|{cur_page + 1}")
                prev_page_button = InlineKeyboardButton("Назад", callback_data=f"{callback_name}|prev|{cur_page + 1}")
                pagination_button = InlineKeyboardButton(f"{cur_page + 2}/{self._n_pages}", callback_data="echo")
                keyboard.add(prev_page_button, pagination_button, next_page_button)
            else:
                prev_page_button = InlineKeyboardButton("Назад", callback_data=f"{callback_name}|prev|{cur_page + 1}")
                keyboard.add(prev_page_button)
        else:
            if cur_page > 1:
                next_page_button = InlineKeyboardButton("Далее", callback_data=f"{callback_name}|next|{cur_page - 1}")
                prev_page_button = InlineKeyboardButton("Назад", callback_data=f"{callback_name}|prev|{cur_page - 1}")
                pagination_button = InlineKeyboardButton(f"{cur_page}/{self._n_pages}", callback_data="echo")
                keyboard.add(prev_page_button, pagination_button, next_page_button)
            else:
                next_page_button = InlineKeyboardButton("Далее", callback_data=f"{callback_name}|next|{cur_page - 1}")
                keyboard.add(next_page_button)

        return keyboard
