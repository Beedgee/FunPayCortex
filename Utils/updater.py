# START OF FILE FunPayCortex/Utils/updater.py

"""
Проверка на обновления (ОТКЛЮЧЕНА).
"""
import time
from logging import getLogger
from locales.localizer import Localizer
import requests
import os
import zipfile
import shutil
import json


logger = getLogger("FPC.update_checker") # Keep logger name?
localizer = Localizer()
_ = localizer.translate

HEADERS = {
    "accept": "application/vnd.github+json"
}


class Release:
    """
    Класс, описывающий релиз.
    """
    def __init__(self, name: str, description: str, sources_link: str):
        """
        :param name: название релиза.
        :param description: описание релиза (список изменений).
        :param sources_link: ссылка на архив с исходниками.
        """
        self.name = name
        self.description = description
        self.sources_link = sources_link


# Получение данных о новом релизе
def get_tags(current_tag: str) -> list[str] | None:
    """
    Получает все теги с GitHub репозитория.
    :param current_tag: текущий тег.

    :return: список тегов.
    """
    # Эта функция больше не нужна для отключения обновлений, но оставляем её структуру
    # на случай, если захочется вернуть обновления или сделать свою систему.
    logger.debug("Update check: get_tags called (effectively disabled).")
    return None # Возвращаем None, имитируя ошибку получения тегов

def get_next_tag(tags: list[str], current_tag: str):
    """
    Ищет след. тег после переданного.
    Если не находит текущий тег, возвращает первый.
    Если текущий тег - последний, возвращает None.

    :param tags: список тегов.
    :param current_tag: текущий тег.

    :return: след. тег / первый тег / None
    """
    # Эта функция больше не нужна для отключения обновлений
    logger.debug("Update check: get_next_tag called (effectively disabled).")
    return None

def get_releases(from_tag: str) -> list[Release] | None:
    """
    Получает данные о доступных релизах, начиная с тега.

    :param from_tag: тег релиза, с которого начинать поиск.

    :return: данные релизов.
    """
    # Эта функция больше не нужна для отключения обновлений
    logger.debug("Update check: get_releases called (effectively disabled).")
    return None

def get_new_releases(current_tag) -> int | list[Release]:
    """
    Проверяет на наличие обновлений. (МОДИФИЦИРОВАНА: Всегда возвращает код 2 - последняя версия)

    :param current_tag: тег текущей версии.

    :return: код ошибки 2 (последняя версия).
    """
    logger.info("Update check skipped (disabled).")
    return 2 # Всегда возвращаем код 2, что означает "установлена последняя версия"


#  Загрузка нового релиза
def download_zip(url: str) -> int:
    """
    Загружает zip архив с обновлением в файл storage/cache/update.zip.
    (Эта функция больше не будет вызываться из-за отключения обновлений).

    :param url: ссылка на zip архив.

    :return: 0, если архив с обновлением загружен, иначе - 1.
    """
    logger.debug(f"Update download attempted for {url} (Updates disabled).")
    return 1 # Возвращаем ошибку, т.к. обновления отключены

def extract_update_archive() -> str | int:
    """
    Разархивирует скачанный update.zip.
    (Эта функция больше не будет вызываться из-за отключения обновлений).

    :return: название папки с обновлением (storage/cache/update/<папка с обновлением>) или 1, если произошла ошибка.
    """
    logger.debug("Update extraction attempted (Updates disabled).")
    return 1 # Возвращаем ошибку

def zipdir(path, zip_obj):
    """
    Рекурсивно архивирует папку.

    :param path: путь до папки.
    :param zip_obj: объект zip архива.
    """
    for root, dirs, files in os.walk(path):
        if os.path.basename(root) == "__pycache__":
            continue
        for file in files:
            zip_obj.write(os.path.join(root, file),
                          os.path.relpath(os.path.join(root, file),
                                          os.path.join(path, '..')))


def create_backup() -> int:
    """
    Создает резервную копию с папками storage и configs.

    :return: 0, если бэкап создан успешно, иначе - 1.
    """
    try:
        with zipfile.ZipFile("backup.zip", "w") as zip:
            zipdir("storage", zip)
            zipdir("configs", zip)
            zipdir("plugins", zip)
        return 0
    except:
        logger.debug("TRACEBACK", exc_info=True)
        return 1


def install_release(folder_name: str) -> int:
    """
    Устанавливает обновление.
    (Эта функция больше не будет вызываться из-за отключения обновлений).

    :param folder_name: название папки со скачанным обновлением в storage/cache/update
    :return: 0, если обновление установлено.
        1 - произошла непредвиденная ошибка.
        2 - папка с обновлением отсутствует.
    """
    logger.debug(f"Update installation attempted from {folder_name} (Updates disabled).")
    return 1 # Возвращаем ошибку

# END OF FILE FunPayCortex/Utils/updater.py