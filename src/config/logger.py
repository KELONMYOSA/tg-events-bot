import json
import logging
import string
import time
import traceback

from datetime import datetime
from typing import Union

import requests

from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

from src.config.config import settings

_APP_NAME = "ITMO_TG_BOT"
_LOKI_URL = settings.LOKI_URL
_LOKI_USER = settings.LOKI_USER
_LOKI_PASSWORD = settings.LOKI_PASSWORD


def push_loki(msg):
    ns = 1e9
    ts = str(int(time.time() * ns))
    stream = {
        "stream": json.loads(msg),
        "values": [[ts, msg]],
    }
    payload = {"streams": [stream]}

    try:
        resp = requests.post(_LOKI_URL, json=payload, auth=HTTPBasicAuth(_LOKI_USER, _LOKI_PASSWORD))
        if resp.status_code != 204:
            raise ValueError(f"Unexpected Loki API response status code: {resp.text}")
    except Exception as e:
        print(f"Error when sending logs to loki: {e}")


def print_console(msg):
    print(log_json_to_line(msg))


class JSONLogFormatter(logging.Formatter):
    """
    Кастомизированный класс-форматер для логов в формате json
    """

    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        log_object: dict = self._format_log_object(record)

        return json.dumps(log_object)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        now = datetime.fromtimestamp(record.created).astimezone().replace(microsecond=0).isoformat()
        message = record.getMessage()

        # Инициализация тела журнала
        log_fields = BaseLogSchema(
            timestamp=now,
            level=record.levelname,
            app_name=_APP_NAME,
            logger=record.name,
            message=message,
        )

        if hasattr(record, 'props'):
            log_fields.props = record.props

        if record.exc_info:
            log_fields.exceptions = traceback.format_exception(*record.exc_info)
        elif record.exc_text:
            log_fields.exceptions = record.exc_text

        # Преобразование Pydantic объекта в словарь
        log_object = log_fields.model_dump(exclude_unset=True)

        # Соединение дополнительных полей логирования
        extra_tags = getattr(record, "tags", {})
        if not isinstance(extra_tags, dict):
            return log_object

        for tag_name, tag_value in extra_tags.items():
            cleared_name = format_label(tag_name)
            if cleared_name:
                log_object[cleared_name] = tag_value

        return log_object


class BaseLogSchema(BaseModel):
    timestamp: str
    level: str
    app_name: str
    logger: str
    message: str
    exceptions: Union[list[str], str] = None


def format_label(label: str) -> str:
    """
    Build label to match prometheus format.

    Label format - https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels
    """
    label_replace_with = (
        ("'", ""),
        ('"', ""),
        (" ", "_"),
        (".", "_"),
        ("-", "_"),
    )
    label_allowed_chars: str = "".join((string.ascii_letters, string.digits, "_"))

    for char_from, char_to in label_replace_with:
        label = label.replace(char_from, char_to)
    return "".join(char for char in label if char in label_allowed_chars)


def log_json_to_line(msg: str) -> str:
    msg_dict: dict = json.loads(msg)
    ex = msg_dict.pop('exceptions', None)
    if ex is not None:
        msg_dict['exceptions'] = str(ex)
    values = list(map(str, msg_dict.values()))

    return " | ".join(values)
