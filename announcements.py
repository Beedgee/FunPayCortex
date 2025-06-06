# START OF FILE FunPayCortex/announcements.py

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from tg_bot.utils import NotificationTypes
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from locales.localizer import Localizer
from threading import Thread
from logging import getLogger
import requests
import json
import os
import time

logger = getLogger("FPC.announcements")
localizer = Localizer()
_ = localizer.translate

def get_announcement(ignore_last_tag: bool = False) -> dict | None:
    """
    Получает информацию об объявлении.
    МОДИФИЦИРОВАНО: Всегда возвращает None, чтобы отключить внешние объявления.
    Если вы захотите использовать свою систему объявлений, вам нужно будет
    изменить эту функцию для получения данных из вашего источника.

    :return: None (объявления из внешнего источника отключены).
    """
    logger.debug("Проверка внешних объявлений отключена. get_announcement всегда возвращает None.")
    return None


def download_photo(url: str) -> bytes | None:
    """
    Загружает фото по URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка загрузки фото {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке фото {url}: {e}")
        return None

def get_notification_type(data: dict) -> NotificationTypes:
    types = {
        0: NotificationTypes.ad,
        1: NotificationTypes.announcement,
        2: NotificationTypes.important_announcement
    }
    return types.get(data.get("type"), NotificationTypes.critical)

def get_photo(data: dict) -> bytes | None:
    if not (photo_url := data.get("ph")):
        return None
    return download_photo(str(photo_url))

def get_text(data: dict) -> str | None:
    if not (text_content := data.get("text")):
        return None
    return str(text_content)

def get_pin(data: dict) -> bool:
    return bool(data.get("pin"))

def get_keyboard(data: dict) -> K | None:
    if not (kb_data := data.get("kb")):
        return None
    kb = K()
    try:
        for row_data in kb_data:
            buttons_in_row = []
            for btn_dict in row_data:
                btn_args_safe = {str(key): str(value) for key, value in btn_dict.items()}
                buttons_in_row.append(B(**btn_args_safe))
            if buttons_in_row:
                kb.row(*buttons_in_row)
    except Exception as e:
        logger.error(f"Ошибка при создании клавиатуры для объявления: {e}")
        return None
    return kb if kb.keyboard else None


def announcements_loop_iteration(cortex_instance: Cortex, ignore_last_tag: bool = False):
    announcement_data = get_announcement(ignore_last_tag=ignore_last_tag)
    if not announcement_data:
        return

    text_content = get_text(announcement_data)
    photo_content = get_photo(announcement_data)
    notification_type_enum = get_notification_type(announcement_data)
    keyboard_markup = get_keyboard(announcement_data)
    should_pin = get_pin(announcement_data)

    if text_content or photo_content:
        Thread(target=cortex_instance.telegram.send_notification,
               args=(text_content,),
               kwargs={"photo": photo_content, 
                       'notification_type': notification_type_enum, 
                       'keyboard': keyboard_markup,
                       'pin': should_pin},
               daemon=True).start()


def announcements_loop(cortex_instance: Cortex):
    """
    Бесконечный цикл получения объявлений. (Эффективно неактивен из-за изменений в get_announcement)
    """
    if not cortex_instance.telegram:
        logger.info("Цикл объявлений не запущен (Telegram не настроен).")
        return

    logger.info("Цикл проверки объявлений запущен (внешние объявления отключены).")
    while True:
        try:
            announcements_loop_iteration(cortex_instance, ignore_last_tag=False)
        except Exception as e:
            logger.error(f"Ошибка в (отключенном) цикле объявлений: {e}")
            logger.debug("TRACEBACK", exc_info=True)
        time.sleep(3600)


def main(cortex_instance: Cortex):
    Thread(target=announcements_loop, args=(cortex_instance,), daemon=True).start()


BIND_TO_POST_INIT = [main]

# END OF FILE FunPayCortex/announcements.py