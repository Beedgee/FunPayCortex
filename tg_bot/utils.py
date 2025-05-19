"""
В данном модуле написаны инструменты, которыми пользуется Telegram бот.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex # Renamed FPCortex to Cortex

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
import configparser
import datetime
import os.path
import json
import time

import Utils.cortex_tools # Renamed from Utils to Utils
from tg_bot import CBT
from locales.localizer import Localizer # Добавляем импорт Localizer

localizer = Localizer() # Инициализируем Localizer
_ = localizer.translate # Создаем алиас для функции перевода

class NotificationTypes:
    """
    Класс с типами Telegram уведомлений.
    (Без изменений)
    """
    bot_start = "1"
    new_message = "2"
    command = "3"
    new_order = "4"
    order_confirmed = "5"
    review = "5r"
    lots_restore = "6"
    lots_deactivate = "7"
    delivery = "8"
    lots_raise = "9"
    other = "10"
    announcement = "11"
    ad = "12"
    critical = "13"
    important_announcement = "14"


def load_authorized_users() -> dict[int, dict[str, bool | None | str]]:
    """
    Загружает авторизированных пользователей из кэша.
    (Логика без изменений, но добавлена обработка случая, если файл пуст или некорректен)
    """
    filepath = "storage/cache/tg_authorized_users.json"
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f) # Используем json.load для корректного чтения
        
        result = {}
        if isinstance(data, list): # Обработка старого формата (список ID)
            for user_id_val in data:
                if isinstance(user_id_val, int): # Убедимся, что это int
                    result[user_id_val] = {} 
            save_authorized_users(result) # Пересохраняем в новом формате
        elif isinstance(data, dict): # Новый формат (словарь)
            for k, v in data.items():
                try: # Преобразуем ключи в int, если они строки
                    result[int(k)] = v
                except ValueError:
                    # Пропускаем некорректные ключи
                    continue
        return result
    except (json.JSONDecodeError, FileNotFoundError): # Если файл пуст, поврежден или не найден
        return {}


def load_notification_settings() -> dict:
    """
    Загружает настройки Telegram уведомлений из кэша.
    (Обработка ошибок при чтении файла)
    """
    filepath = "storage/cache/notifications.json"
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def load_answer_templates() -> list[str]:
    """
    Загружает шаблоны ответов из кэша.
    (Обработка ошибок при чтении файла)
    """
    filepath = "storage/cache/answer_templates.json"
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            templates = json.load(f)
            # Убедимся, что это список строк
            return [str(item) for item in templates if isinstance(item, (str, int, float))] if isinstance(templates, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_authorized_users(users: dict[int, dict]) -> None:
    """
    Сохраняет ID авторизированных пользователей.
    (Без изменений в логике, но убедимся что директория создана)
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True) # exist_ok=True чтобы не было ошибки если папка уже есть
    with open(os.path.join(dir_path, "tg_authorized_users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4) # ensure_ascii=False для кириллицы, indent для читаемости


def save_notification_settings(settings: dict) -> None:
    """
    Сохраняет настройки Telegram-уведомлений.
    (Улучшено сохранение JSON)
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "notifications.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def save_answer_templates(templates: list[str]) -> None:
    """
    Сохраняет шаблоны ответов.
    (Улучшено сохранение JSON)
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "answer_templates.json"), "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=4)


def escape(text: str) -> str:
    """
    Форматирует текст под HTML разметку.
    (Без изменений)
    """
    if not isinstance(text, str): # Добавим проверку типа на всякий случай
        text = str(text)
    escape_characters = {
        "&": "&",
        "<": "<",
        ">": ">",
    }
    for char, escaped_char in escape_characters.items():
        text = text.replace(char, escaped_char)
    return text

# Функция split_by_limit не используется напрямую для вывода пользователю, оставляем без изменений
def split_by_limit(list_of_str: list[str], limit: int = 4096):
    result = []
    current_chunk = ""
    for s_item in list_of_str:
        if len(current_chunk) + len(s_item) + 1 > limit: # +1 для возможного \n
            result.append(current_chunk)
            current_chunk = s_item
        else:
            if current_chunk: # Добавляем разделитель, если это не начало чанка
                current_chunk += "\n" + s_item
            else:
                current_chunk = s_item
    if current_chunk: # Добавляем последний чанк
        result.append(current_chunk)
    return result


def bool_to_text(value: bool | int | str | None, on: str = "🟢", off: str = "🔴"):
    """
    Преобразует булево значение или его представление в текстовый статус с эмодзи.
    (Без изменений, так как эмодзи уже хорошие)
    """
    if value is not None:
        try:
            if int(value):
                return on
        except ValueError: # Если value - строка, которую нельзя привести к int
            pass # Оставляем off по умолчанию
    return off


def get_offset(element_index: int, max_elements_on_page: int) -> int:
    """
    Возвращает смещение списка элементов таким образом, чтобы элемент с индексом element_index оказался в конце списка.
    (Без изменений)
    """
    elements_amount = element_index + 1
    elements_on_page = elements_amount % max_elements_on_page
    elements_on_page = elements_on_page if elements_on_page else max_elements_on_page
    if not elements_amount - elements_on_page:
        return 0
    else:
        return element_index - elements_on_page + 1


def add_navigation_buttons(keyboard_obj: K, curr_offset: int,
                           max_elements_on_page: int,
                           elements_on_page: int, elements_amount: int,
                           callback_text: str,
                           extra: list | None = None) -> K:
    """
    Добавляет к переданной клавиатуре кнопки след. / пред. страница.
    (Тексты кнопок навигации теперь из локализации)
    """
    extra_cb_part = (":" + ":".join(str(i) for i in extra)) if extra else ""
    
    # Кнопки для перехода на первую и последнюю страницы
    first_page_cb = f"{callback_text}:0{extra_cb_part}" if curr_offset > 0 else CBT.EMPTY
    
    # Рассчитываем смещение для последней страницы
    # Если элементов 0, то и страниц 0, last_page_offset не нужен
    last_page_offset = 0
    if elements_amount > 0:
        num_pages = math.ceil(elements_amount / max_elements_on_page)
        last_page_offset = (num_pages - 1) * max_elements_on_page if num_pages > 0 else 0
    
    last_page_cb = f"{callback_text}:{last_page_offset}{extra_cb_part}" if curr_offset + elements_on_page < elements_amount else CBT.EMPTY

    # Кнопки для перехода на предыдущую и следующую страницы
    prev_page_offset = max(0, curr_offset - max_elements_on_page)
    prev_page_cb = f"{callback_text}:{prev_page_offset}{extra_cb_part}" if curr_offset > 0 else CBT.EMPTY
    
    next_page_offset = curr_offset + elements_on_page
    next_page_cb = f"{callback_text}:{next_page_offset}{extra_cb_part}" if curr_offset + elements_on_page < elements_amount else CBT.EMPTY

    # Отображение текущей страницы и общего количества страниц
    current_page_num = (curr_offset // max_elements_on_page) + 1
    total_pages_num = math.ceil(elements_amount / max_elements_on_page) if elements_amount > 0 else 1
    
    page_info_text = f"{current_page_num}/{total_pages_num}"

    nav_buttons = []
    if curr_offset > 0 : # Показываем кнопки "назад", если это не первая страница
        nav_buttons.append(B("⏪", callback_data=first_page_cb)) # Первая страница
        nav_buttons.append(B(_("gl_back").split(' ')[0], callback_data=prev_page_cb)) # Пред. страница, берем только эмодзи или первое слово из "Назад ◀️"

    nav_buttons.append(B(page_info_text, callback_data=CBT.EMPTY)) # Номер страницы

    if curr_offset + elements_on_page < elements_amount: # Показываем кнопки "вперед", если это не последняя страница
        nav_buttons.append(B(_("gl_next").split(' ')[0], callback_data=next_page_cb)) # След. страница, берем только эмодзи или первое слово из "Далее ▶️"
        nav_buttons.append(B("⏩", callback_data=last_page_cb)) # Последняя страница
    
    if len(nav_buttons) > 1: # Добавляем ряд навигации, только если есть хотя бы одна кнопка кроме номера страницы
        keyboard_obj.row(*nav_buttons)
    return keyboard_obj


def generate_profile_text(cortex_instance: Cortex) -> str:
    """
    Генерирует текст с информацией об аккаунте.
    (Используем локализованные строки)
    """
    account = cortex_instance.account
    balance = cortex_instance.balance
    # Локализация заголовков и полей
    # Заголовок: Информация об аккаунте {username}
    # ID: {id}
    # Незавершенных заказов: {active_sales}
    # Баланс:
    #   RUB: {total_rub}₽ (доступно: {available_rub}₽)
    #   USD: {total_usd}$ (доступно: {available_usd}$)
    #   EUR: {total_eur}€ (доступно: {available_eur}€)
    # Обновлено: {last_update_time}

    profile_header = _("cmd_profile") # "посмотреть статистику аккаунта" - можно изменить на "Статистика аккаунта"
    if "посмотреть" in profile_header: # Убираем глагол, если он есть
        profile_header = profile_header.split(" ",1)[1].capitalize()

    return f"""📊 <b>{profile_header} «{escape(account.username)}»</b>

🆔 <b>ID:</b> <code>{account.id}</code>
🛒 <b>{_('ntfc_new_order').split(':')[0].replace('💰 ','')}:</b> <code>{account.active_sales}</code> 
{_('fpc_init').splitlines()[3].split(':')[0].strip()}:
    🇷🇺 <b>RUB:</b> <code>{balance.total_rub}₽</code> ({_('acc_balance_available', language=localizer.current_language)} <code>{balance.available_rub}₽</code>)
    🇺🇸 <b>USD:</b> <code>{balance.total_usd}$</code> ({_('acc_balance_available', language=localizer.current_language)} <code>{balance.available_usd}$</code>)
    🇪🇺 <b>EUR:</b> <code>{balance.total_eur}€</code> ({_('acc_balance_available', language=localizer.current_language)} <code>{balance.available_eur}€</code>)

⏱️ <i>{_('gl_last_update')}:</i> <code>{time.strftime('%H:%M:%S %d.%m.%Y', time.localtime(account.last_update))}</code>"""
    # Добавил ключ 'acc_balance_available' = "доступно" для локализации

def generate_lot_info_text(lot_obj: configparser.SectionProxy) -> str:
    """
    Генерирует текст с информацией о лоте.
    (Используем локализованные строки)
    """
    # Определяем текст для файла товаров
    products_file_name = lot_obj.get("productsFileName")
    file_info_text = ""
    products_amount_text = f"<code>∞</code> ({_('gf_infinity', language=localizer.current_language)})" # Ключ для "бесконечно"

    if products_file_name:
        full_file_path = os.path.join("storage", "products", products_file_name)
        file_info_text = f"<code>{escape(full_file_path)}</code>"
        if os.path.exists(full_file_path):
            try:
                count = Utils.cortex_tools.count_products(full_file_path)
                products_amount_text = f"<code>{count}</code>"
            except Exception:
                products_amount_text = f"<code>⚠️</code> ({_('gf_count_error', language=localizer.current_language)})" # Ключ для "ошибка подсчета"
        else: # Файл указан, но не существует
            file_info_text += f" ({_('gf_file_not_found_short', language=localizer.current_language)})" # Ключ для "не найден"
            products_amount_text = "<code>-</code>" # Прочерк, так как файла нет
            # Создаем пустой файл, если он указан в конфиге, но отсутствует физически
            try:
                if not os.path.exists(os.path.dirname(full_file_path)):
                     os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                with open(full_file_path, "w", encoding="utf-8"): pass
                file_info_text += f" ({_('gf_file_created_now', language=localizer.current_language)})" # Ключ для "создан сейчас"
            except Exception as e:
                file_info_text += f" ({_('gf_file_creation_error_short', language=localizer.current_language)})" # Ключ для "ошибка создания"

    else:
        file_info_text = f"<i>({_('gf_not_linked', language=localizer.current_language)})</i>" # Ключ для "не привязан"

    # Локализация заголовков и текста
    # Информация о лоте: {lot_name}
    # Текст выдачи: {response_text}
    # Количество товаров: {products_count}
    # Файл с товарами: {file_path_info}
    # Обновлено: {update_time}
    
    return f"""📦 <b>{_('lot_info_header', language=localizer.current_language)}: «{escape(lot_obj.name)}»</b>

📜 <b>{_('ea_edit_delivery_text').replace('✏️ ','')}:</b>
<code>{escape(lot_obj.get("response", _("text_not_set", language=localizer.current_language)))}</code>

🔢 <b>{_('gf_amount')}:</b> {products_amount_text}
🗂️ <b>{_('ea_link_goods_file').replace('🔗 ','')}:</b> {file_info_text}

⏱️ <i>{_('gl_last_update')}:</i> <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"""
# Добавлены ключи для локализации:
# 'acc_balance_available'
# 'gf_infinity'
# 'gf_count_error'
# 'gf_file_not_found_short'
# 'gf_file_created_now'
# 'gf_file_creation_error_short'
# 'gf_not_linked'
# 'lot_info_header'
# 'text_not_set'