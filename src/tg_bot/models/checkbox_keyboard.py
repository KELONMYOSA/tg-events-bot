from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class CheckboxKeyboard:
    def __init__(self, callback_name: str, data: dict[str: bool], row_width: int = 1):
        self._callback_name = callback_name
        self._data = data
        self._row_width = row_width

    def create_keyboard(self) -> InlineKeyboardMarkup:
        buttons = []

        for n, (text, status) in enumerate(self._data.items()):
            if status:
                button_text = f"✅ {text}"
            else:
                button_text = text
            buttons.append(InlineKeyboardButton(text=button_text, callback_data=f"{self._callback_name}|select|{n}]"))

        ok_button = InlineKeyboardButton("ОК", callback_data=f"{self._callback_name}|ok")
        keyboard = InlineKeyboardMarkup().add(*buttons, row_width=self._row_width).add(ok_button)

        return keyboard

    @staticmethod
    def get_selected_buttons(markup: InlineKeyboardMarkup) -> list[str]:
        keyboard = markup.keyboard
        buttons_list = [button for sublist in keyboard for button in sublist]
        selected_texts = []
        for button in buttons_list:
            if "✅" in button.text:
                selected_texts.append(button.text.replace("✅ ", ""))

        return selected_texts

    @staticmethod
    def change_button_selection(markup: InlineKeyboardMarkup, callback: str) -> InlineKeyboardMarkup:
        keyboard = markup.keyboard
        for i, row in enumerate(keyboard, start=0):
            for j, button in enumerate(row, start=0):
                if button.callback_data != callback:
                    continue
                else:
                    if "✅" in button.text:
                        button.text = button.text.replace("✅ ", "")
                    else:
                        button.text = "✅ " + button.text
                    keyboard[i][j] = button

                    return InlineKeyboardMarkup(keyboard)
