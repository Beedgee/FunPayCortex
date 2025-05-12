# START OF FILE FunPayCortex/Utils/cortex_tools.py

from __future__ import annotations
from typing import TYPE_CHECKING

import bcrypt
import requests

from locales.localizer import Localizer

if TYPE_CHECKING:
    from cortex import Cortex # Renamed from Cardinal

import FunPayAPI.types

from datetime import datetime
import Utils.exceptions
import itertools
import psutil
import json
import sys
import os
import re
import time
import logging

PHOTO_RE = re.compile(r'\$photo=[\d]+')
ENTITY_RE = re.compile(r"\$photo=\d+|\$new|(\$sleep=(\d+\.\d+|\d+))")
logger = logging.getLogger("FPCortex.cortex_tools") # Renamed logger
localizer = Localizer()
_ = localizer.translate


def count_products(path: str) -> int:
    """
    Подсчитывает количество товаров в указанном файле.

    :param path: путь к файлу с товарами.

    :return: количество товаров.
    """
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        products = f.read()
    products = products.split("\n")
    products = list(itertools.filterfalse(lambda el: not el, products))
    return len(products)


def cache_blacklist(blacklist: list[str]) -> None:
    """
    Кэширует черный список пользователей.

    :param blacklist: черный список.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/blacklist.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(blacklist, indent=4, ensure_ascii=False))


def load_blacklist() -> list[str]:
    """
    Загружает черный список из кэша.

    :return: черный список.
    """
    if not os.path.exists("storage/cache/blacklist.json"):
        return []

    with open("storage/cache/blacklist.json", "r", encoding="utf-8") as f:
        blacklist_data = f.read() # Renamed variable

        try:
            blacklist = json.loads(blacklist_data)
        except json.decoder.JSONDecodeError:
            return []
        return blacklist


def check_proxy(proxy: dict) -> bool:
    """
    Проверяет работоспособность прокси-сервера.

    :param proxy: словарь с данными прокси.

    :return: True, если прокси работает, иначе - False.
    """
    logger.info(_("crd_checking_proxy"))
    try:
        response = requests.get("https://api.ipify.org/", proxies=proxy, timeout=10)
        response.raise_for_status() # Check for HTTP errors
    except requests.exceptions.RequestException as e: # Catch specific requests exceptions
        logger.error(_("crd_proxy_err"))
        logger.debug(f"Proxy check error: {e}", exc_info=True)
        return False
    except Exception as e: # Catch any other unexpected errors
        logger.error(_("crd_proxy_err"))
        logger.debug(f"Unexpected proxy check error: {e}", exc_info=True)
        return False

    logger.info(_("crd_proxy_success", response.content.decode()))
    return True


def validate_proxy(proxy: str):
    """
    Проверяет прокси на соответствие формату IPv4 и возвращает логин, пароль, IP и порт,
    либо выбрасывает исключение.

    :param proxy: строка с данными прокси.
    :return: кортеж (логин, пароль, IP, порт).
    :raises ValueError: если формат прокси некорректен.
    """
    try:
        if "@" in proxy:
            login_password, ip_port = proxy.split("@", 1) # Split only once
            if ":" not in login_password:
                 login, password = login_password, "" # Handle cases like user@ip:port (no password)
            else:
                 login, password = login_password.split(":", 1) # Split only once
            ip, port_str = ip_port.split(":", 1) # Renamed port to port_str
        else:
            login, password = "", ""
            ip, port_str = proxy.split(":", 1) # Renamed port to port_str

        port = int(port_str) # Convert port to int after splitting

        # IP validation: checks for 4 octets, all digits, and values between 0-255
        octets = ip.split(".")
        if len(octets) != 4 or not all(octet.isdigit() and 0 <= int(octet) <= 255 for octet in octets):
            raise ValueError("Некорректный формат IP-адреса.")

        # Port validation
        if not (0 <= port <= 65535):
            raise ValueError("Некорректный номер порта.")

    except ValueError as e: # Catch specific ValueError for format issues
        raise ValueError(f"Некорректный формат прокси: {proxy}. Ожидается 'ip:port' или 'login:password@ip:port'. Детали: {e}")
    except Exception as e: # Catch any other splitting/conversion errors
        raise ValueError(f"Ошибка разбора строки прокси: {proxy}. Детали: {e}")
    return login, password, ip, port


def cache_proxy_dict(proxy_dict: dict[int, str]) -> None:
    """
    Кэширует словарь прокси.

    :param proxy_dict: словарь прокси.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/proxy_dict.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(proxy_dict, indent=4, ensure_ascii=False))


def load_proxy_dict() -> dict[int, str]:
    """
    Загружает словарь прокси из кэша.

    :return: словарь прокси.
    """
    if not os.path.exists("storage/cache/proxy_dict.json"):
        return {}

    with open("storage/cache/proxy_dict.json", "r", encoding="utf-8") as f:
        proxy_data = f.read() # Renamed variable

        try:
            proxy_dict_loaded = json.loads(proxy_data)
            # Ensure keys are integers after loading from JSON
            proxy_dict_loaded = {int(k): v for k, v in proxy_dict_loaded.items()}
        except json.decoder.JSONDecodeError:
            return {}
        return proxy_dict_loaded


def cache_disabled_plugins(disabled_plugins: list[str]) -> None:
    """
    Кэширует UUID отключенных плагинов.

    :param disabled_plugins: список UUID отключенных плагинов.
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")

    with open("storage/cache/disabled_plugins.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(disabled_plugins, ensure_ascii=False))


def load_disabled_plugins() -> list[str]:
    """
    Загружает список UUID отключенных плагинов из кэша.

    :return: список UUID отключенных плагинов.
    """
    if not os.path.exists("storage/cache/disabled_plugins.json"):
        return []

    with open("storage/cache/disabled_plugins.json", "r", encoding="utf-8") as f:
        try:
            return json.loads(f.read())
        except json.decoder.JSONDecodeError:
            return []


def cache_old_users(old_users: dict[int, float]):
    """
    Сохраняет в кэш список пользователей, которые уже писали на аккаунт (с временными метками).
    """
    if not os.path.exists("storage/cache"):
        os.makedirs("storage/cache")
    with open(f"storage/cache/old_users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(old_users, ensure_ascii=False, indent=4))


def load_old_users(greetings_cooldown_days: float) -> dict[int, float]:
    """
    Загружает из кэша список пользователей, которые уже писали на аккаунт,
    фильтруя тех, чей кулдаун приветствия истек.

    :param greetings_cooldown_days: кулдаун приветствия в днях.
    :return: словарь {ID чата: timestamp последнего приветствия}.
    """
    greetings_cooldown_seconds = greetings_cooldown_days * 24 * 60 * 60
    if not os.path.exists(f"storage/cache/old_users.json"):
        return {}
    try:
        with open(f"storage/cache/old_users.json", "r", encoding="utf-8") as f:
            users_data = json.loads(f.read())
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return {}

    current_time = time.time()
    filtered_users = {}

    if isinstance(users_data, list): # Handle old format (list of user IDs)
        for user_id in users_data:
            filtered_users[int(user_id)] = current_time # Assume they were greeted now
        cache_old_users(filtered_users) # Cache in new format
        return filtered_users
    elif isinstance(users_data, dict):
        for user_id_str, timestamp in users_data.items():
            try:
                user_id = int(user_id_str)
                if current_time - timestamp < greetings_cooldown_seconds:
                    filtered_users[user_id] = timestamp
            except ValueError:
                logger.warning(f"Некорректный ID пользователя '{user_id_str}' в old_users.json, пропускается.")
        # Пересохраняем отфильтрованный список, чтобы удалить устаревшие записи
        if len(filtered_users) != len(users_data):
            cache_old_users(filtered_users)
        return filtered_users
    else:
        return {}


def create_greeting_text(cortex_instance: Cortex) -> str:
    """
    Генерирует приветственный текст для вывода в консоль после загрузки данных о пользователе.
    """
    account = cortex_instance.account
    balance = cortex_instance.balance
    current_time = datetime.now()

    if current_time.hour < 4:
        greetings = "🌌 Доброй ночи"
    elif current_time.hour < 12:
        greetings = "☀️ Доброе утро"
    elif current_time.hour < 17:
        greetings = "🌤️ Добрый день"
    else:
        greetings = "🌙 Добрый вечер"

    lines = [
        f"✨ {greetings}, $CYAN{account.username}$RESET!",
        f"🆔 Ваш ID: $YELLOW{account.id}$RESET.",
        f"💰 Баланс: $CYAN{balance.total_rub:.2f} ₽$RESET | $MAGENTA{balance.total_usd:.2f} $$RESET | $YELLOW{balance.total_eur:.2f} €$RESET.",
        f"📈 Активные сделки: $YELLOW{account.active_sales}$RESET.",
        f"🚀 Удачной торговли и высокой прибыли!"
    ]

    max_line_len = 0
    for line in lines:
        # Убираем ANSI коды для подсчета реальной длины
        clean_line = re.sub(r'\$[A-Z]+', '', line) # Упрощенное удаление, можно улучшить
        max_line_len = max(max_line_len, len(clean_line))

    length = max(60, max_line_len + 4) # Динамическая ширина рамки
    border_char = "═"
    side_char = "║"

    greeting_text = f"\n$GREEN╔{border_char * (length-2)}╗$RESET\n"
    for line in lines:
        clean_line_len = len(re.sub(r'\$[A-Z]+', '', line))
        padding = length - clean_line_len - 4
        greeting_text += f"$GREEN{side_char}$RESET {line}{' ' * padding}$GREEN{side_char}$RESET\n"
    greeting_text += f"$GREEN╚{border_char * (length-2)}╝$RESET\n"
    return greeting_text


def time_to_str(time_seconds: int) -> str: # Renamed variable for clarity
    """
    Конвертирует количество секунд в строку формата "Хд Хч Хмин Хсек".

    :param time_seconds: количество секунд для конвертации.
    :return: строка, представляющая время.
    """
    if not isinstance(time_seconds, (int, float)) or time_seconds < 0:
        return "0 сек"

    time_seconds = int(time_seconds)

    days = time_seconds // 86400
    time_seconds %= 86400
    hours = time_seconds // 3600
    time_seconds %= 3600
    minutes = time_seconds // 60
    seconds = time_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}д")
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0:
        parts.append(f"{minutes}мин")
    if seconds > 0 or not parts: # Показываем секунды, если это единственная единица времени или есть другие
        parts.append(f"{seconds}сек")

    return " ".join(parts) if parts else "0 сек"


def get_month_name(month_number: int, case: str = "gent") -> str: # Added case parameter
    """
    Возвращает название месяца. По умолчанию в родительном падеже.

    :param month_number: номер месяца (1-12).
    :param case: падеж ('nomn' - именительный, 'gent' - родительный).
    :return: название месяца.
    """
    months_nomn = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июля", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    months_gent = [
        "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
        "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
    ]

    if not 1 <= month_number <= 12:
        logger.warning(f"Некорректный номер месяца: {month_number}. Возвращен январь.")
        month_number = 1

    if case == "nomn":
        return months_nomn[month_number - 1]
    elif case == "gent":
        return months_gent[month_number - 1]
    else:
        logger.warning(f"Неизвестный падеж: {case}. Возвращен родительный.")
        return months_gent[month_number - 1]


def get_products(path: str, amount: int = 1) -> tuple[list[str], int] | None:
    """
    Извлекает указанное количество товаров из файла, удаляя их оттуда.

    :param path: путь к файлу с товарами.
    :param amount: количество товаров для извлечения.
    :return: кортеж ([Список извлеченных товаров], оставшееся количество товаров в файле) или None при ошибке.
    :raises Utils.exceptions.NoProductsError: если файл пуст.
    :raises Utils.exceptions.NotEnoughProductsError: если товаров в файле меньше, чем запрошено.
    """
    try:
        with open(path, "r+", encoding="utf-8") as f: # Open in r+ for reading and writing
            lines = f.readlines()
            products = [line.strip() for line in lines if line.strip()] # Убираем пустые строки и строки с пробелами

            if not products:
                raise Utils.exceptions.NoProductsError(path)
            if len(products) < amount:
                raise Utils.exceptions.NotEnoughProductsError(path, len(products), amount)

            got_products = products[:amount]
            remaining_products = products[amount:]

            f.seek(0) # Возвращаемся в начало файла
            f.writelines(p + "\n" for p in remaining_products) # Записываем оставшиеся товары
            f.truncate() # Удаляем все, что было после записанных строк (на случай, если новый контент короче)

        return got_products, len(remaining_products)
    except FileNotFoundError:
        logger.error(f"Файл товаров не найден: {path}")
        return None
    except (Utils.exceptions.NoProductsError, Utils.exceptions.NotEnoughProductsError):
        raise # Пробрасываем специфичные исключения дальше
    except Exception as e:
        logger.error(f"Ошибка при работе с файлом товаров {path}: {e}")
        logger.debug("TRACEBACK", exc_info=True)
        return None


def add_products(path: str, products_to_add: list[str], at_zero_position=False): # Renamed parameter
    """
    Добавляет товары в файл.

    :param path: путь к файлу с товарами.
    :param products_to_add: список товаров для добавления.
    :param at_zero_position: True - добавить в начало, False - добавить в конец.
    """
    try:
        if not os.path.exists(os.path.dirname(path)) and os.path.dirname(path):
             os.makedirs(os.path.dirname(path))

        if at_zero_position:
            current_products = []
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    current_products = [line.strip() for line in f if line.strip()]
            
            all_products = products_to_add + current_products
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(p + "\n" for p in all_products)
        else:
            with open(path, "a", encoding="utf-8") as f:
                if os.path.getsize(path) > 0: # Добавляем новую строку только если файл не пустой
                     f.write("\n")
                f.writelines(p + "\n" for p in products_to_add)
        logger.info(f"Добавлено {len(products_to_add)} товаров в файл: {path}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении товаров в файл {path}: {e}")
        logger.debug("TRACEBACK", exc_info=True)


def safe_text(text: str) -> str:
    """
    Экранирует текст для безопасного отображения (например, в HTML в Telegram).
    Заменяет специальные символы на их HTML-эквиваленты.
    Использует невидимый символ для предотвращения форматирования Markdown/HTML в никнеймах.
    """
    if not isinstance(text, str):
        return ""
    # Символ нулевой ширины для "разрыва" форматирования Markdown/HTML
    zero_width_char = "\u2063" # INVISIBLE SEPARATOR (U+2063)
    
    # Экранирование HTML
    escaped_text = text.replace("&", "&").replace("<", "<").replace(">", ">")
    
    # Добавление невидимого разделителя между каждым символом оригинального текста
    # чтобы затруднить копирование и предотвратить нежелательное форматирование ников
    safe_display_text = zero_width_char.join(escaped_text)
    
    return safe_display_text


def format_msg_text(text_template: str, obj: FunPayAPI.types.Message | FunPayAPI.types.ChatShortcut) -> str: # Renamed parameter
    """
    Форматирует текст, подставляя значения переменных, доступных для MessageEvent.

    :param text_template: шаблон текста для форматирования.
    :param obj: экземпляр types.Message или types.ChatShortcut.
    :return: форматированный текст.
    """
    now = datetime.now()
    
    username_raw = obj.author if isinstance(obj, FunPayAPI.types.Message) else obj.name
    chat_name_raw = obj.chat_name if isinstance(obj, FunPayAPI.types.Message) else obj.name
    chat_id_str = str(obj.chat_id) if isinstance(obj, FunPayAPI.types.Message) else str(obj.id)
    message_text_raw = str(obj)

    variables = {
        "$full_date_text": now.strftime(f"%d {get_month_name(now.month, 'gent')} %Y года"),
        "$date_text": now.strftime(f"%d {get_month_name(now.month, 'gent')}"),
        "$date": now.strftime("%d.%m.%Y"),
        "$time": now.strftime("%H:%M"),
        "$full_time": now.strftime("%H:%M:%S"),
        "$username": safe_text(username_raw or "Неизвестный"), # Добавлена проверка на None
        "$message_text": message_text_raw, # Не экранируем, т.к. это текст сообщения, может содержать разметку
        "$chat_id": chat_id_str,
        "$chat_name": safe_text(chat_name_raw or "Неизвестный") # Добавлена проверка на None
    }

    formatted_text = text_template
    for var, value in variables.items():
        formatted_text = formatted_text.replace(var, value)
    return formatted_text


def format_order_text(text_template: str, order: FunPayAPI.types.OrderShortcut | FunPayAPI.types.Order) -> str: # Renamed parameter
    """
    Форматирует текст, подставляя значения переменных, доступных для Order.

    :param text_template: шаблон текста для форматирования.
    :param order: экземпляр Order.
    :return: форматированный текст.
    """
    now = datetime.now()
    game, subcategory_fullname, subcategory_name_str = "", "", "" # Renamed subcategory to subcategory_name_str

    try:
        if order.subcategory:
            subcategory_fullname = order.subcategory.fullname
            game = order.subcategory.category.name
            subcategory_name_str = order.subcategory.name
        elif isinstance(order, FunPayAPI.types.OrderShortcut) and order.subcategory_name:
            # Попытка разделить "Игра, Категория"
            parts = order.subcategory_name.rsplit(", ", 1)
            if len(parts) == 2:
                game, subcategory_name_str = parts
            else:
                subcategory_name_str = order.subcategory_name # Если не удалось разделить, используем как есть
            subcategory_fullname = f"{subcategory_name_str} {game}".strip()
        else:
            logger.warning(f"Не удалось определить игру/категорию для заказа #{order.id}")
    except Exception as e:
        logger.warning(f"Ошибка при парсинге игры/категории из заказа #{order.id}: {e}")
        logger.debug("TRACEBACK", exc_info=True)

    description = order.description if isinstance(order, FunPayAPI.types.OrderShortcut) else (order.short_description or "")
    params_text = order.lot_params_text if isinstance(order, FunPayAPI.types.Order) and order.lot_params else ""
    buyer_username_raw = order.buyer_username or "Покупатель"

    order_desc_and_params = f"{description}, {params_text}" if description and params_text else f"{description}{params_text}"

    variables = {
        "$full_date_text": now.strftime(f"%d {get_month_name(now.month, 'gent')} %Y года"),
        "$date_text": now.strftime(f"%d {get_month_name(now.month, 'gent')}"),
        "$date": now.strftime("%d.%m.%Y"),
        "$time": now.strftime("%H:%M"),
        "$full_time": now.strftime("%H:%M:%S"),
        "$username": safe_text(buyer_username_raw),
        "$order_desc_and_params": order_desc_and_params,
        "$order_desc_or_params": description or params_text,
        "$order_desc": description,
        "$order_title": description, # Алиас для $order_desc
        "$order_params": params_text,
        "$order_id": order.id,
        "$order_link": f"https://funpay.com/orders/{order.id}/",
        "$category_fullname": subcategory_fullname,
        "$category": subcategory_name_str,
        "$game": game
    }

    formatted_text = text_template
    for var, value in variables.items():
        formatted_text = formatted_text.replace(var, str(value)) # Убедимся что все значения строки
    return formatted_text


def restart_program():
    """
    Полностью перезапускает FPCortex.
    """
    logger.info("🚀 Инициирован перезапуск FPCortex...")
    try:
        python_executable = sys.executable
        os.execl(python_executable, python_executable, *sys.argv)
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка при попытке перезапуска: {e}")
        logger.debug("TRACEBACK", exc_info=True)
        # Попытка закрыть ресурсы, если execl не сработал (маловероятно)
        try:
            process = psutil.Process()
            for handler in process.open_files() + process.connections():
                try:
                    os.close(handler.fd)
                except OSError:
                    pass
        except Exception as e_psutil:
            logger.error(f"Ошибка при закрытии ресурсов psutil: {e_psutil}")


def shut_down():
    """
    Полностью останавливает FPCortex.
    """
    logger.info("🔌 Инициировано выключение FPCortex...")
    try:
        process = psutil.Process()
        # Сначала пытаемся мягко завершить
        process.terminate()
        try:
            # Ждем недолго, затем принудительно, если нужно
            process.wait(timeout=5)
        except psutil.TimeoutExpired:
            logger.warning("Процесс не завершился штатно, принудительное завершение...")
            process.kill()
        logger.info("💤 FPCortex успешно остановлен.")
    except psutil.NoSuchProcess:
        logger.info("💤 Процесс FPCortex уже был остановлен.")
    except Exception as e:
        logger.error(f"💥 Ошибка при выключении FPCortex: {e}")
        logger.debug("TRACEBACK", exc_info=True)


def set_console_title(title: str) -> None:
    """
    Изменяет заголовок консоли (для Windows).
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
    except ImportError:
        logger.debug("Модуль ctypes не найден, заголовок консоли не будет изменен (не критично).")
    except Exception as e:
        logger.warning(f"Произошла ошибка при изменении заголовка консоли: {e}")
        logger.debug("TRACEBACK", exc_info=True)


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.

    :param password: пароль в виде строки.
    :return: хешированный пароль в виде строки.
    """
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password_bytes.decode('utf-8')


def check_password(password: str, hashed_password_str: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль хешированному.

    :param password: пароль для проверки (строка).
    :param hashed_password_str: сохраненный хеш пароля (строка).
    :return: True, если пароли совпадают, иначе False.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password_str.encode('utf-8'))
    except ValueError: # Может возникнуть, если hashed_password_str невалидный bcrypt хеш
        logger.error("Ошибка при проверке пароля: невалидный формат хеша.")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке пароля: {e}")
        return False

# END OF FILE FunPayCortex/Utils/cortex_tools.py