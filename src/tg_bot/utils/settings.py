from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.tg_bot.models.checkbox_keyboard import CheckboxKeyboard
from src.tg_bot.models.dictionaries import topic2domain, topic2name
from src.tg_bot.utils.dao import PostgreDB


def notification_interval_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    interval_texts = ["Ежедневно", "Каждые 3 дня", "Раз в неделю", "Раз в 2 недели", "Никогда"]
    buttons = []
    for n, text in enumerate(interval_texts):
        buttons.append(InlineKeyboardButton(text, callback_data=f"{callback_data}|{n}"))
    keyboard = InlineKeyboardMarkup().add(*buttons, row_width=2)

    return keyboard


n_button2interval = {
    0: 1,
    1: 3,
    2: 7,
    3: 14,
    4: 0,
}

n_button2text = {
    0: "Уведомления будут приходить ежедневно",
    1: "Уведомления будут приходить каждые 3 дня",
    2: "Уведомления будут приходить каждую неделю",
    3: "Уведомления будут приходить раз в 2 недели",
    4: "Уведомления отключены",
}


def domain_selection_keyboard(user_id: int, callback_data: str) -> InlineKeyboardMarkup:
    with PostgreDB() as db:
        user_domains = db.get_user_domains(user_id)

    domain_selection = {}
    for domain in topic2domain.values():
        topic = list(filter(lambda x: topic2domain[x] == domain, topic2domain))[0]
        text = topic2name[topic]

        if not user_domains:
            domain_selection[text] = True
            continue

        if domain in user_domains:
            domain_selection[text] = True
        else:
            domain_selection[text] = False

    domains_keyboard = CheckboxKeyboard(callback_data, domain_selection, 2).create_keyboard()

    return domains_keyboard


def provider_selection_keyboard(user_id: int, callback_data: str) -> InlineKeyboardMarkup:
    with PostgreDB() as db:
        user_providers = db.get_user_providers(user_id)

    with PostgreDB() as db:
        providers = db.get_providers()
    id2provider_name = {}
    for provider in providers:
        id2provider_name[provider.id] = provider.name

    provider_selection = {}
    for provider_id in id2provider_name:
        text = id2provider_name[provider_id]

        if not user_providers:
            provider_selection[text] = True
            continue

        if provider_id in user_providers:
            provider_selection[text] = True
        else:
            provider_selection[text] = False

    provider_keyboard = CheckboxKeyboard(callback_data, provider_selection).create_keyboard()

    return provider_keyboard
