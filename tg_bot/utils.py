# START OF FILE FunPayCortex/tg_bot/utils.py

"""
В данном модуле написаны инструменты, которыми пользуется Telegram бот.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
import configparser
import datetime
import os.path
import json
import time

import Utils.cortex_tools
from tg_bot import CBT
from locales.localizer import Localizer

localizer = Localizer()
_ = localizer.translate

class NotificationTypes:
    """
    Класс с типами Telegram уведомлений.
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


def load_authorized_users() -> dict[int, dict[str, str | None]]:
    """
    Загружает авторизированных пользователей из кэша.
    Формат: {user_id: {"username": "...", "role": "admin" | "manager"}}
    """
    filepath = "storage/cache/tg_authorized_users.json"
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {}
        if isinstance(data, list):  # Migration from old list format
            for user_id_val in data:
                if isinstance(user_id_val, int):
                    result[user_id_val] = {"username": None, "role": "admin"}
            save_authorized_users(result)  # Save in new format
            return result
        elif isinstance(data, dict):
            for k, v in data.items():
                try:
                    user_id = int(k)
                    if isinstance(v, dict):
                        result[user_id] = {
                            "username": v.get("username"),
                            "role": v.get("role")
                        }
                    else:  # Migration from another old dict format
                        result[user_id] = {"username": str(v) if v else None, "role": "admin"}
                except (ValueError, TypeError):
                    continue
            return result
        return {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def load_notification_settings() -> dict:
    """
    Загружает настройки Telegram уведомлений из кэша.
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
    """
    filepath = "storage/cache/answer_templates.json"
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            templates = json.load(f)
            return [str(item) for item in templates if isinstance(item, (str, int, float))] if isinstance(templates, list) else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_authorized_users(users: dict[int, dict]) -> None:
    """
    Сохраняет ID и роли авторизированных пользователей.
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "tg_authorized_users.json"), "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def save_notification_settings(settings: dict) -> None:
    """
    Сохраняет настройки Telegram-уведомлений.
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "notifications.json"), "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def save_answer_templates(templates: list[str]) -> None:
    """
    Сохраняет шаблоны ответов.
    """
    dir_path = "storage/cache/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "answer_templates.json"), "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=4)


def get_user_role(users_dict: dict, user_id: int) -> str | None:
    """Возвращает роль пользователя ('admin', 'manager') или None."""
    user_data = users_dict.get(user_id)
    if user_data and isinstance(user_data, dict):
        return user_data.get("role")
    return None


def escape(text: str) -> str:
    """
    Форматирует текст под HTML разметку.
    """
    if not isinstance(text, str):
        text = str(text)
    escape_characters = {
        "&": "&",
        "<": "<",
        ">": ">",
    }
    for char, escaped_char in escape_characters.items():
        text = text.replace(char, escaped_char)
    return text

def split_by_limit(list_of_str: list[str], limit: int = 4096):
    result = []
    current_chunk = ""
    for s_item in list_of_str:
        if len(current_chunk) + len(s_item) + 1 > limit:
            result.append(current_chunk)
            current_chunk = s_item
        else:
            if current_chunk:
                current_chunk += "\n" + s_item
            else:
                current_chunk = s_item
    if current_chunk:
        result.append(current_chunk)
    return result


def bool_to_text(value: bool | int | str | None, on: str = "🟢", off: str = "🔴"):
    """
    Преобразует булево значение или его представление в текстовый статус с эмодзи.
    """
    if value is not None:
        try:
            if int(value):
                return on
        except (ValueError, TypeError):
            pass
    return off


def get_offset(element_index: int, max_elements_on_page: int) -> int:
    """
    Возвращает смещение списка элементов таким образом, чтобы элемент с индексом element_index оказался в конце списка.
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
    """
    extra_cb_part = (":" + ":".join(str(i) for i in extra)) if extra else ""
    
    first_page_cb = f"{callback_text}:0{extra_cb_part}" if curr_offset > 0 else CBT.EMPTY
    
    last_page_offset = 0
    if elements_amount > 0:
        num_pages = math.ceil(elements_amount / max_elements_on_page)
        last_page_offset = (num_pages - 1) * max_elements_on_page if num_pages > 0 else 0
    
    last_page_cb = f"{callback_text}:{last_page_offset}{extra_cb_part}" if curr_offset + elements_on_page < elements_amount else CBT.EMPTY

    prev_page_offset = max(0, curr_offset - max_elements_on_page)
    prev_page_cb = f"{callback_text}:{prev_page_offset}{extra_cb_part}" if curr_offset > 0 else CBT.EMPTY
    
    next_page_offset = curr_offset + elements_on_page
    next_page_cb = f"{callback_text}:{next_page_offset}{extra_cb_part}" if curr_offset + elements_on_page < elements_amount else CBT.EMPTY

    current_page_num = (curr_offset // max_elements_on_page) + 1
    total_pages_num = math.ceil(elements_amount / max_elements_on_page) if elements_amount > 0 else 1
    
    page_info_text = f"{current_page_num}/{total_pages_num}"

    nav_buttons = []
    if curr_offset > 0 :
        nav_buttons.append(B("⏪", callback_data=first_page_cb))
        nav_buttons.append(B(_("gl_back").split(' ')[-1], callback_data=prev_page_cb))

    nav_buttons.append(B(page_info_text, callback_data=CBT.EMPTY))

    if curr_offset + elements_on_page < elements_amount:
        nav_buttons.append(B(_("gl_next").split(' ')[0], callback_data=next_page_cb))
        nav_buttons.append(B("⏩", callback_data=last_page_cb))
    
    if len(nav_buttons) > 1:
        keyboard_obj.row(*nav_buttons)
    return keyboard_obj


def generate_profile_text(cortex_instance: Cortex) -> str:
    """
    Генерирует текст с информацией об аккаунте.
    """
    account = cortex_instance.account
    balance = cortex_instance.balance

    profile_header = _("cmd_profile")
    if "посмотреть" in profile_header.lower():
        profile_header = profile_header.split(" ",1)[1].capitalize()
    elif "переглянути" in profile_header.lower():
        profile_header = profile_header.split(" ",1)[1].capitalize()
    elif "view" in profile_header.lower():
         profile_header = profile_header.split(" ",1)[1].capitalize()

    active_orders_label_key = "ns_new_order"
    active_orders_label_full = _(active_orders_label_key)
    active_orders_text = active_orders_label_full.split(" ", 1)[1] if "{}" in active_orders_label_full.split(" ", 1)[0] else active_orders_label_full

    fpc_init_text = _('fpc_init')
    balance_label_text_raw = ""
    for line in fpc_init_text.splitlines():
        if "₽" in line and "$" in line and "€" in line and "Баланс:" in line:
            parts = line.split("<code>",1)
            if parts:
                balance_label_text_raw = parts[0].strip()
            break
    if not balance_label_text_raw or "Баланс" not in balance_label_text_raw:
        balance_label_text_raw = "<b><i>" + _("mm_balance") + ":</i></b>"


    return f"""📊 <b>{profile_header} «{escape(account.username)}»</b>

🆔 <b>ID:</b> <code>{account.id}</code>
🛒 <b>{active_orders_text}:</b> <code>{account.active_sales}</code>
{balance_label_text_raw}
    🇷🇺 <b>RUB:</b> <code>{balance.total_rub}₽</code> ({_('acc_balance_available')} <code>{balance.available_rub}₽</code>)
    🇺🇸 <b>USD:</b> <code>{balance.total_usd}$</code> ({_('acc_balance_available')} <code>{balance.available_usd}$</code>)
    🇪🇺 <b>EUR:</b> <code>{balance.total_eur}€</code> ({_('acc_balance_available')} <code>{balance.available_eur}€</code>)

⏱️ {_('gl_last_update')}: <code>{time.strftime('%H:%M:%S %d.%m.%Y', time.localtime(account.last_update))}</code>"""

def generate_lot_info_text(lot_obj: configparser.SectionProxy) -> str:
    """
    Генерирует текст с информацией о лоте.
    """
    products_file_name = lot_obj.get("productsFileName")
    file_info_text = ""
    products_amount_text = f"<code>∞</code> ({_('gf_infinity')})"

    if products_file_name:
        full_file_path = os.path.join("storage", "products", products_file_name)
        file_info_text = f"<code>{escape(full_file_path)}</code>"
        if os.path.exists(full_file_path):
            try:
                count = Utils.cortex_tools.count_products(full_file_path)
                products_amount_text = f"<code>{count}</code>"
            except Exception:
                products_amount_text = f"<code>⚠️</code> ({_('gf_count_error')})"
        else:
            file_info_text += f" ({_('gf_file_not_found_short')})"
            products_amount_text = "<code>-</code>"
            try:
                if not os.path.exists(os.path.dirname(full_file_path)):
                     os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                with open(full_file_path, "w", encoding="utf-8"): pass
                file_info_text += f" ({_('gf_file_created_now')})"
            except Exception as e:
                file_info_text += f" ({_('gf_file_creation_error_short')})"

    else:
        file_info_text = f"<i>({_('gf_not_linked')})</i>"

    
    return f"""📦 <b>{_('lot_info_header')}: «{escape(lot_obj.name)}»</b>

📜 <b>{_('ea_edit_delivery_text').replace('✏️ ','')}:</b>
<code>{escape(lot_obj.get("response", _("text_not_set")))}</code>

🔢 <b>{_('gf_amount')}:</b> {products_amount_text}
🗂️ <b>{_('ea_link_goods_file').replace('🔗 ','')}:</b> {file_info_text}

⏱️ {_('gl_last_update')}: <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"""


def generate_advanced_stats_text(cortex_instance: Cortex, stats: dict) -> str:
    """
    Генерирует текст с расширенной статистикой аккаунта.
    """
    account = cortex_instance.account
    balance = cortex_instance.balance
    
    def format_price_dict(price_dict: dict) -> str:
        if not price_dict:
            return "0 ¤"
        return ", ".join([f"{v:,.2f}".replace(",", " ") + f" {k}" for k, v in sorted(price_dict.items())])

    def format_sales_tuple(sales_tuple: tuple) -> str:
        count, price_dict = sales_tuple
        return f"{count} ({format_price_dict(price_dict)})"

    period_days = stats.get('parsing_period', 30)
    
    text = f"""📊 <b>Статистика аккаунта «{escape(account.username)}»</b>
🆔 <b>ID:</b> <code>{account.id}</code>
💰 <b>Баланс:</b> <code>{balance.total_rub:,.2f} ₽, {balance.total_usd:,.2f} $, {balance.total_eur:,.2f} €</code>
🛒 <b>Незавершенных заказов:</b> <code>{account.active_sales}</code>

<b>Доступно для вывода:</b>
  ▫️ <i>Сейчас:</i> <code>{balance.available_rub:,.2f} ₽, {balance.available_usd:,.2f} $, {balance.available_eur:,.2f} €</code>
  ▫️ <i>Через час:</i> <code>+{format_price_dict(stats['withdraw']['hour'])}</code>
  ▫️ <i>Через день:</i> <code>+{format_price_dict(stats['withdraw']['day'])}</code>
  ▫️ <i>Через 2 дня:</i> <code>+{format_price_dict(stats['withdraw']['two_days'])}</code>

📈 <b>Товаров продано:</b>
  ▫️ <i>За день:</i> <code>{format_sales_tuple(stats['sales']['day'])}</code>
  ▫️ <i>За неделю:</i> <code>{format_sales_tuple(stats['sales']['week'])}</code>
  ▫️ <i>За месяц:</i> <code>{format_sales_tuple(stats['sales']['month'])}</code>
  ▫️ <i>За период ({period_days} дн.):</i> <code>{format_sales_tuple(stats['sales']['period'])}</code>

📉 <b>Товаров возвращено:</b>
  ▫️ <i>За день:</i> <code>{format_sales_tuple(stats['refunds']['day'])}</code>
  ▫️ <i>За неделю:</i> <code>{format_sales_tuple(stats['refunds']['week'])}</code>
  ▫️ <i>За месяц:</i> <code>{format_sales_tuple(stats['refunds']['month'])}</code>
  ▫️ <i>За период ({period_days} дн.):</i> <code>{format_sales_tuple(stats['refunds']['period'])}</code>

⏱️ {_('gl_last_update')}: <code>{datetime.datetime.now().strftime('%H:%M:%S')}</code>
"""
    return text.replace(",", " ")

# END OF FILE FunPayCortex/tg_bot/utils.py