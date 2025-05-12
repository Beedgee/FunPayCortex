# START OF FILE FunPayCortex/announcements.py

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cardinal # Will be renamed later

from tg_bot.utils import NotificationTypes
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from locales.localizer import Localizer
from threading import Thread
from logging import getLogger
import requests
import json
import os
import time

logger = getLogger("FPC.announcements") # Keep logger name?
localizer = Localizer()
_ = localizer.translate


def get_last_tag() -> str | None:
    """
    Загружает тег последнего объявления из кэша.
    (Функция больше не используется, т.к. объявления отключены)

    :return: тег последнего объявления или None, если его нет.
    """
    if not os.path.exists("storage/cache/announcement_tag.txt"):
        return None
    with open("storage/cache/announcement_tag.txt", "r", encoding="UTF-8") as f:
        data = f.read()
    return data


REQUESTS_DELAY = 600
# LAST_TAG = get_last_tag() # Больше не нужно


def save_last_tag():
    """
    Сохраняет тег последнего объявления в кэш.
    (Функция больше не используется)
    """
    # global LAST_TAG
    # if not os.path.exists("storage/cache"):
    #     os.makedirs("storage/cache")
    # with open("storage/cache/announcement_tag.txt", "w", encoding="UTF-8") as f:
    #     f.write(LAST_TAG)
    pass


def get_announcement(ignore_last_tag: bool = False) -> dict | None:
    """
    Получает информацию об объявлении. (МОДИФИЦИРОВАНО: Всегда возвращает None)
    Если тэг объявления совпадает с сохраненным тегом и ignore_last_tag ложь, возвращает None.
    Если произошла ошибка при получении объявлении, возвращает None.

    :return: None (объявления отключены).
    """
    logger.debug("Announcements check skipped (disabled).")
    return None # Всегда возвращаем None


def download_photo(url: str) -> bytes | None:
    """
    Загружает фото по URL.
    (Функция больше не используется)

    :param url: URL фотографии.

    :return: фотографию в виде массива байтов.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
    except:
        return None
    return response.content


# Разбор данных объявления (эти функции больше не будут вызываться)
def get_notification_type(data: dict) -> NotificationTypes:
    """
    Находит данные о типе объявления.
    0 - реклама.
    1 - объявление.
    Другое - критическое объявление.

    :param data: данные объявления.

    :return: тип уведомления.
    """
    types = {
        0: NotificationTypes.ad,
        1: NotificationTypes.announcement,
        2: NotificationTypes.important_announcement
    }
    return types[data.get("type")] if data.get("type") in types else NotificationTypes.critical


def get_photo(data: dict) -> bytes | None:
    """
    Загружает фотографию по ссылке, если она есть в данных об объявлении.

    :param data: данные объявления.

    :return: фотографию в виде массива байтов или None, если ссылка на фото не найдена или загрузка не удалась.
    """
    if not (photo := data.get("ph")):
        return None
    return download_photo(u"{}".format(photo))


def get_text(data: dict) -> str | None:
    """
    Находит данные о тексте объявления.

    :param data: данные объявления.

    :return: текст объявления или None, если он не найден.
    """
    if not (text := data.get("text")):
        return None
    return u"{}".format(text)


def get_pin(data: dict) -> bool:
    """
    Получает информацию о том, нужно ли закреплять объявление.

    :param data: данные объявления.

    :return: True / False.
    """
    return bool(data.get("pin"))


def get_keyboard(data: dict) -> K | None:
    """
    Получает информацию о клавиатуре и генерирует ее.
    Пример клавиатуры:

    :param data: данные объявления.

    :return: объект клавиатуры или None, если данные о ней не найдены.
    """
    if not (kb_data := data.get("kb")):
        return None

    kb = K()
    try:
        for row in kb_data:
            buttons = []
            for btn in row:
                btn_args = {u"{}".format(i): u"{}".format(btn[i]) for i in btn}
                buttons.append(B(**btn_args))
            kb.row(*buttons)
    except:
        return None
    return kb


def announcements_loop_iteration(cortex_instance: Cardinal, ignore_last_tag: bool = False): # Renamed var
    # global LAST_TAG # Not needed
    # Эта функция больше не будет делать ничего полезного, т.к. get_announcement всегда None
    if not (data := get_announcement(ignore_last_tag=ignore_last_tag)):
        # time.sleep(REQUESTS_DELAY) # No need to sleep if we don't fetch
        return

    # The code below will not be reached because get_announcement returns None
    # if not ignore_last_tag:
    #     LAST_TAG = data.get("tag")
    #     save_last_tag()
    # text = get_text(data)
    # photo = get_photo(data)
    # notification_type = get_notification_type(data)
    # keyboard = get_keyboard(data)
    # pin = get_pin(data)

    # if text or photo:
    #     Thread(target=cortex_instance.telegram.send_notification,
    #            args=(text,),
    #            kwargs={"photo": photo, 'notification_type': notification_type, 'keyboard': keyboard,
    #                    'pin': pin},
    #            daemon=True).start()


def announcements_loop(cortex_instance: Cardinal): # Renamed var
    """
    Бесконечный цикл получения объявлений. (ОТКЛЮЧЕН)
    """
    if not cortex_instance.telegram:
        logger.info("Announcements loop disabled (Telegram not configured).")
        return

    logger.info("Announcements loop started (effectively disabled).")
    while True:
        try:
            # Эта итерация ничего не будет делать
            announcements_loop_iteration(cortex_instance, ignore_last_tag=False)
        except Exception as e: # Catch potential errors even if disabled
             logger.error(f"Error in disabled announcements loop: {e}")
             logger.debug("TRACEBACK", exc_info=True)
        # Sleep for a longer interval since it's disabled
        time.sleep(3600) # Sleep for an hour


def main(cortex_instance: Cardinal): # Renamed var
    # Запускаем цикл в отдельном потоке, но он будет неактивен
    Thread(target=announcements_loop, args=(cortex_instance,), daemon=True).start()


BIND_TO_POST_INIT = [main]

# END OF FILE FunPayCortex/announcements.py