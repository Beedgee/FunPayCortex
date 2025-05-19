# START OF FILE FunPayCortex/cortex.py # Renamed file

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from FunPayAPI import types
from FunPayAPI.common.enums import SubCategoryTypes

if TYPE_CHECKING:
    from configparser import ConfigParser

from tg_bot import auto_response_cp, config_loader_cp, auto_delivery_cp, templates_cp, plugins_cp, file_uploader, \
    authorized_users_cp, proxy_cp, default_cp
from types import ModuleType
import Utils.exceptions
from uuid import UUID
import importlib.util
import configparser
import itertools
import requests
import datetime
import logging
import random
import time
import sys
import os
from pip._internal.cli.main import main
import FunPayAPI
import handlers
import announcements # Re-enabled announcements
from locales.localizer import Localizer
from FunPayAPI import utils as fp_utils
from Utils import cardinal_tools # Keep filename for now
import tg_bot.bot

from threading import Thread

logger = logging.getLogger("FPC") # Keep logger name?
localizer = Localizer()
_ = localizer.translate


def get_cortex() -> None | Cortex: # Renamed function
    """
    Возвращает существующий экземпляр кортекса.
    """
    if hasattr(Cortex, "instance"):
        return getattr(Cortex, "instance")


class PluginData:
    """
    Класс, описывающий плагин.
    """

    def __init__(self, name: str, version: str, desc: str, credentials: str, uuid: str,
                 path: str, plugin: ModuleType, settings_page: bool, delete_handler: Callable | None, enabled: bool):
        """
        :param name: название плагина.
        :param version: версия плагина.
        :param desc: описание плагина.
        :param credentials: авторы плагина.
        :param uuid: UUID плагина.
        :param path: путь до плагина.
        :param plugin: экземпляр плагина как модуля.
        :param settings_page: есть ли страница настроек у плагина.
        :param delete_handler: хэндлер, привязанный к удалению плагина.
        :param enabled: включен ли плагин.
        """
        self.name = name
        self.version = version
        self.description = desc
        self.credits = credentials
        self.uuid = uuid

        self.path = path
        self.plugin = plugin
        self.settings_page = settings_page
        self.commands = {}
        self.delete_handler = delete_handler
        self.enabled = enabled


class Cortex(object): # Renamed class
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Cortex, cls).__new__(cls) # Renamed class
        return getattr(cls, "instance")

    def __init__(self, main_config: ConfigParser,
                 auto_delivery_config: ConfigParser,
                 auto_response_config: ConfigParser,
                 raw_auto_response_config: ConfigParser,
                 version: str):
        self.VERSION = version
        self.instance_id = random.randint(0, 999999999)
        self.delivery_tests = {}  # Одноразовые ключи для тестов автовыдачи. {"ключ": "название лота"}

        # Конфиги
        self.MAIN_CFG = main_config
        self.AD_CFG = auto_delivery_config
        self.AR_CFG = auto_response_config
        self.RAW_AR_CFG = raw_auto_response_config
        # Прокси
        self.proxy = {}
        self.proxy_dict = cardinal_tools.load_proxy_dict()  # прокси {0: "login:password@ip:port", 1: "ip:port"...}
        if self.MAIN_CFG["Proxy"].getboolean("enable"):
            if self.MAIN_CFG["Proxy"]["ip"] and self.MAIN_CFG["Proxy"]["port"].isnumeric():
                logger.info(_("crd_proxy_detected"))

                ip, port = self.MAIN_CFG["Proxy"]["ip"], self.MAIN_CFG["Proxy"]["port"]
                login, password = self.MAIN_CFG["Proxy"]["login"], self.MAIN_CFG["Proxy"]["password"]
                proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
                self.proxy = {
                    "http": f"http://{proxy_str}",
                    "https": f"http://{proxy_str}"
                }

                if proxy_str not in self.proxy_dict.values():
                    max_id = max(self.proxy_dict.keys(), default=-1)
                    self.proxy_dict[max_id + 1] = proxy_str
                    cardinal_tools.cache_proxy_dict(self.proxy_dict)

                if self.MAIN_CFG["Proxy"].getboolean("check") and not cardinal_tools.check_proxy(self.proxy):
                    sys.exit()

        self.account = FunPayAPI.Account(self.MAIN_CFG["FunPay"]["golden_key"],
                                         self.MAIN_CFG["FunPay"]["user_agent"],
                                         proxy=self.proxy)
        self.runner: FunPayAPI.Runner | None = None
        self.telegram: tg_bot.bot.TGBot | None = None

        self.running = False
        self.run_id = 0
        self.start_time = int(time.time())

        self.balance: FunPayAPI.types.Balance | None = None
        self.raise_time = {}  # Временные метки поднятия категорий {id игры: след. время поднятия}
        self.raised_time = {}  # Время последнего поднятия категории {id игры: время последнего поднятия}
        self.__exchange_rates = {}  # Курс валют {(валюта1, валюта2): (курс, время обновления)}
        self.profile: FunPayAPI.types.UserProfile | None = None  # FunPay профиль для всего кортекса (+ хэндлеров) # Renamed comment
        self.tg_profile: FunPayAPI.types.UserProfile | None = None  # FunPay профиль (для Telegram-ПУ)
        self.last_tg_profile_update = datetime.datetime.now()  # Последнее время обновления профиля для TG-ПУ
        self.curr_profile: FunPayAPI.types.UserProfile | None = None  # Текущий профиль (для восст. / деакт. лотов.)
        # Тег последнего event'а, после которого обновлялся self.current_profile
        self.curr_profile_last_tag: str | None = None
        # Тег последнего event'а, после которого в self.profile добавлялись отсутствующие ранее лоты
        self.profile_last_tag: str | None = None
        # Тег последнего event'а, после которого обновлялось состояние лотов.
        self.last_state_change_tag: str | None = None
        self.blacklist = cardinal_tools.load_blacklist()  # ЧС.
        self.old_users = cardinal_tools.load_old_users(
            float(self.MAIN_CFG["Greetings"]["greetingsCooldown"]))  # Уже написавшие пользователи.

        # Хэндлеры
        self.pre_init_handlers = []
        self.post_init_handlers = []
        self.pre_start_handlers = []
        self.post_start_handlers = []
        self.pre_stop_handlers = []
        self.post_stop_handlers = []

        self.init_message_handlers = []
        self.messages_list_changed_handlers = []
        self.last_chat_message_changed_handlers = []
        self.new_message_handlers = []
        self.init_order_handlers = []
        self.orders_list_changed_handlers = []
        self.new_order_handlers = []
        self.order_status_changed_handlers = []

        self.pre_delivery_handlers = []
        self.post_delivery_handlers = []

        self.pre_lots_raise_handlers = []
        self.post_lots_raise_handlers = []

        self.handler_bind_var_names = {
            "BIND_TO_PRE_INIT": self.pre_init_handlers,
            "BIND_TO_POST_INIT": self.post_init_handlers,
            "BIND_TO_PRE_START": self.pre_start_handlers,
            "BIND_TO_POST_START": self.post_start_handlers,
            "BIND_TO_PRE_STOP": self.pre_stop_handlers,
            "BIND_TO_POST_STOP": self.post_stop_handlers,
            "BIND_TO_INIT_MESSAGE": self.init_message_handlers,
            "BIND_TO_MESSAGES_LIST_CHANGED": self.messages_list_changed_handlers,
            "BIND_TO_LAST_CHAT_MESSAGE_CHANGED": self.last_chat_message_changed_handlers,
            "BIND_TO_NEW_MESSAGE": self.new_message_handlers,
            "BIND_TO_INIT_ORDER": self.init_order_handlers,
            "BIND_TO_NEW_ORDER": self.new_order_handlers,
            "BIND_TO_ORDERS_LIST_CHANGED": self.orders_list_changed_handlers,
            "BIND_TO_ORDER_STATUS_CHANGED": self.order_status_changed_handlers,
            "BIND_TO_PRE_DELIVERY": self.pre_delivery_handlers,
            "BIND_TO_POST_DELIVERY": self.post_delivery_handlers,
            "BIND_TO_PRE_LOTS_RAISE": self.pre_lots_raise_handlers,
            "BIND_TO_POST_LOTS_RAISE": self.post_lots_raise_handlers,
        }

        self.plugins: dict[str, PluginData] = {}
        self.disabled_plugins = cardinal_tools.load_disabled_plugins()

    def __init_account(self) -> None:
        """
        Инициализирует класс аккаунта (self.account)
        """
        while True:
            try:
                self.account.get()
                self.balance = self.get_balance()
                greeting_text = cardinal_tools.create_greeting_text(self)
                cardinal_tools.set_console_title(f"FunPay Cortex - {self.account.username} ({self.account.id})") # Changed title
                for line in greeting_text.split("\n"):
                    logger.info(line)
                break
            except TimeoutError:
                logger.error(_("crd_acc_get_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str())
                logger.debug(f"TRACEBACK {e.short_str()}")
            except:
                logger.error(_("crd_acc_get_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)

    def __update_profile(self, infinite_polling: bool = True, attempts: int = 0, update_telegram_profile: bool = True,
                         update_main_profile: bool = True) -> bool:
        """
        Загружает данные о лотах категориях аккаунта

        :param infinite_polling: бесконечно посылать запросы, пока не будет получен ответ (игнорировать макс. кол-во
        попыток)
        :param attempts: максимальное кол-во попыток.
        :param update_telegram_profile: обновить ли информацию о профиле для TG ПУ?
        :param update_main_profile: обновить ли информацию о профиле для всего кортекса (+ хэндлеров)? # Renamed comment

        :return: True, если информация обновлена, False, если превышено макс. кол-во попыток.
        """
        logger.info(_("crd_getting_profile_data"))
        # Получаем категории аккаунта.
        current_attempts = 0
        max_attempts = attempts if not infinite_polling else float('inf')


        while current_attempts < max_attempts:
            try:
                profile = self.account.get_user(self.account.id)
                break
            except TimeoutError:
                logger.error(_("crd_profile_get_timeout_err"))
            except FunPayAPI.exceptions.RequestFailedError as e:
                logger.error(e.short_str())
                logger.debug(e)
            except:
                logger.error(_("crd_profile_get_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            
            current_attempts += 1
            if current_attempts >= max_attempts and not infinite_polling:
                 logger.error(_("crd_profile_get_too_many_attempts_err", attempts))
                 return False
            
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)
        else: # Этот блок выполнится, если цикл завершился из-за attempts < max_attempts (т.е. не было break)
            if not infinite_polling: # Только если не бесконечный опрос, это будет ошибкой
                logger.error(_("crd_profile_get_too_many_attempts_err", attempts))
                return False
            # Если infinite_polling и цикл завершился (что не должно произойти без break), это ошибка
            logger.critical("Критическая ошибка в логике __update_profile с infinite_polling.")
            return False


        if update_main_profile:
            self.profile = profile
            self.curr_profile = profile
            self.lots_ids = [i.id for i in profile.get_lots()]
            logger.info(_("crd_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        if update_telegram_profile:
            self.tg_profile = profile
            self.last_telegram_lots_update = datetime.datetime.now()
            logger.info(_("crd_tg_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        return True

    def __init_telegram(self) -> None:
        """
        Инициализирует Telegram бота.
        """
        self.telegram = tg_bot.bot.TGBot(self)
        self.telegram.init()

    def get_balance(self, attempts: int = 3) -> FunPayAPI.types.Balance:
        subcategories = self.account.get_sorted_subcategories()[FunPayAPI.enums.SubCategoryTypes.COMMON]
        lots = []
        
        if not subcategories:
             raise Exception("Нет общих подкатегорий для определения баланса.")

        current_attempts = 0
        while current_attempts < attempts:
            try:
                subcat_id = random.choice(list(subcategories.keys()))
                lots = self.account.get_subcategory_public_lots(FunPayAPI.enums.SubCategoryTypes.COMMON, subcat_id)
                if lots:
                    break
            except Exception as e:
                 logger.warning(f"Ошибка получения лотов для проверки баланса (ПодКат ID: {subcat_id}): {e}")
                 time.sleep(1) 
            current_attempts +=1
            
        if not lots:
             raise Exception(f"Не удалось найти публичные лоты для определения баланса после {attempts} попыток.")

        balance = self.account.get_balance(random.choice(lots).id)
        return balance

    # Прочее
    def raise_lots(self) -> int:
        """
        Пытается поднять лоты.

        :return: предположительное время, когда нужно снова запустить данную функцию.
        """
        next_call = float("inf")

        # Сортируем категории по их позиции для консистентного порядка поднятия
        # Сначала создаем список уникальных объектов категорий
        unique_categories = []
        seen_category_ids = set()
        for subcat in self.profile.get_sorted_lots(2).keys():
            if subcat.category.id not in seen_category_ids:
                unique_categories.append(subcat.category)
                seen_category_ids.add(subcat.category.id)
        
        sorted_categories_to_raise = sorted(unique_categories, key=lambda cat: cat.position)


        for category_obj in sorted_categories_to_raise:
            # Пропускаем, если время поднятия для этой категории еще не настало
            if (saved_raise_time := self.raise_time.get(category_obj.id)) and saved_raise_time > int(time.time()):
                next_call = min(next_call, saved_raise_time)
                continue

            # Проверяем, есть ли вообще COMMON подкатегории у этой игры в профиле пользователя
            # Это важно, так как raise_lots ожидает хотя бы одну подкатегорию
            common_subcats_for_this_game = [
                sc for sc_list in self.profile.get_sorted_lots(2).values() 
                for sc in (sc_list.keys() if isinstance(sc_list, dict) else [sc_list]) # sc_list может быть словарем лотов или одним лотом
                if isinstance(sc, FunPayAPI.types.SubCategory) and sc.type == SubCategoryTypes.COMMON and sc.category.id == category_obj.id
            ]
            # Уникализируем подкатегории, если вдруг дубликаты из-за структуры get_sorted_lots(2)
            unique_common_subcats = list(set(sc.id for sc in common_subcats_for_this_game))


            if not unique_common_subcats:
                logger.debug(f"У категории '{category_obj.name}' нет активных COMMON лотов для поднятия, пропускаем.")
                self.raise_time[category_obj.id] = int(time.time()) + 7200 # Ставим стандартный кулдаун, чтобы не проверять часто
                next_call = min(next_call, self.raise_time[category_obj.id])
                continue


            raise_ok = False
            error_text_msg = "" # Переименовал, чтобы не конфликтовать с модулем
            time_delta_str = "" # Переименовал

            # Пробуем поднять лоты
            try:
                time.sleep(random.uniform(0.5, 1.5)) # Небольшая случайная задержка
                
                # Передаем только ID тех подкатегорий, которые есть у пользователя в данной игре
                self.account.raise_lots(category_obj.id, subcategories=unique_common_subcats)
                
                logger.info(_("crd_lots_raised", category_obj.name))
                raise_ok = True
                last_raised_timestamp = self.raised_time.get(category_obj.id)
                current_timestamp = int(time.time())
                self.raised_time[category_obj.id] = current_timestamp
                
                if last_raised_timestamp:
                    time_delta_str = f" Последнее поднятие: {cardinal_tools.time_to_str(current_timestamp - last_raised_timestamp)} назад."
                
                # Устанавливаем следующий таймер поднятия (например, через 2 часа)
                # Можно сделать это настраиваемым
                next_raise_attempt_time = current_timestamp + 7200 # 2 часа в секундах
                self.raise_time[category_obj.id] = next_raise_attempt_time
                next_call = min(next_call, next_raise_attempt_time)

            except FunPayAPI.exceptions.RaiseError as e:
                error_text_msg = e.error_message if e.error_message else "Неизвестная ошибка FunPay."
                wait_duration = e.wait_time if e.wait_time is not None else 60 # По умолчанию 60 секунд, если время не указано
                
                logger.warning(_("crd_raise_time_err", category_obj.name, error_text_msg,
                                 cardinal_tools.time_to_str(wait_duration)))
                next_raise_attempt_time = int(time.time()) + wait_duration
                
                self.raise_time[category_obj.id] = next_raise_attempt_time
                next_call = min(next_call, next_raise_attempt_time)
                # Не продолжаем, если была ошибка FunPay RaiseError
            
            except Exception as e:
                default_retry_delay = 60
                error_log_message = _("crd_raise_unexpected_err", category_obj.name)
                
                if isinstance(e, FunPayAPI.exceptions.RequestFailedError) and e.status_code in (503, 403, 429):
                    error_log_message = _("crd_raise_status_code_err", e.status_code, category_obj.name)
                    default_retry_delay = 120 # Увеличиваем задержку для серьезных ошибок
                
                logger.error(error_log_message)
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(random.uniform(default_retry_delay / 2, default_retry_delay)) # Случайная задержка перед следующей попыткой
                
                next_raise_attempt_time = int(time.time()) + 1 # Пробуем скоро, но не сразу
                next_call = min(next_call, next_raise_attempt_time)
            
            # Вызываем хендлеры только если было успешное поднятие или ошибка RaiseError (чтобы обработать wait_time)
            if raise_ok or isinstance(e, FunPayAPI.exceptions.RaiseError):
                 self.run_handlers(self.post_lots_raise_handlers, (self, category_obj, error_text_msg + time_delta_str))

        return next_call if next_call < float("inf") else 300 # Если нечего поднимать, проверяем через 5 минут

    def get_order_from_object(self, obj: types.OrderShortcut | types.Message | types.ChatShortcut,
                              order_id_str: str | None = None) -> None | types.Order: # Renamed order_id to order_id_str
        if obj._order_attempt_error:
            return None # Возвращаем None если уже была ошибка
        if obj._order_attempt_made and obj._order is not None: # Если уже успешно получили
            return obj._order
        if obj._order_attempt_made and obj._order is None: # Если пытались, но не получили (например, в процессе)
            # Ждем немного, если другой поток уже получает этот ордер
            wait_count = 0
            while obj._order is None and not obj._order_attempt_error and wait_count < 50: # Таймаут ожидания 5 сек
                time.sleep(0.1)
                wait_count +=1
            return obj._order # Возвращаем что есть (может быть None если таймаут или ошибка)

        obj._order_attempt_made = True # Помечаем, что попытка началась
        
        if not isinstance(obj, (types.Message, types.ChatShortcut, types.OrderShortcut)):
            obj._order_attempt_error = True
            logger.error(f"Неправильный тип объекта для get_order_from_object: {type(obj)}")
            return None

        final_order_id = order_id_str
        if not final_order_id:
            if isinstance(obj, types.OrderShortcut):
                final_order_id = obj.id
                if final_order_id == "ADTEST": # Тестовый заказ, не запрашиваем
                    obj._order_attempt_error = True
                    return None
            elif isinstance(obj, (types.Message, types.ChatShortcut)):
                # Ищем ID заказа в тексте сообщения
                match = fp_utils.RegularExpressions().ORDER_ID.search(str(obj))
                if not match:
                    obj._order_attempt_error = True
                    return None
                final_order_id = match.group(0)[1:] # Убираем '#'

        if not final_order_id: # Если ID заказа все еще не найден
            obj._order_attempt_error = True
            return None

        for attempt_num in range(3, 0, -1): # 3 попытки
            try:
                fetched_order = self.account.get_order(final_order_id)
                obj._order = fetched_order # Сохраняем полученный ордер
                logger.info(f"Получена информация о заказе #{final_order_id}")
                return fetched_order
            except Exception as e:
                logger.warning(f"Ошибка при получении заказа #{final_order_id} (попытка {4-attempt_num}): {e}")
                logger.debug("TRACEBACK", exc_info=True)
                if attempt_num > 1: time.sleep(random.uniform(0.5, 1.5)) # Пауза перед повтором
        
        obj._order_attempt_error = True # Все попытки исчерпаны
        return None

    @staticmethod
    def split_text(text: str) -> list[str]:
        """
        Разбивает текст на суб-тексты по 20 строк.
        """
        output = []
        lines = text.split("\n")
        while lines:
            subtext = "\n".join(lines[:20])
            del lines[:20]
            if (strip := subtext.strip()) and strip != "[a][/a]":
                output.append(subtext)
        return output

    def parse_message_entities(self, msg_text: str) -> list[str | int | float]:
        """
        Разбивает сообщения по 20 строк, отделяет изображения от текста.
        (обозначение изображения: $photo=1234567890)

        :param msg_text: текст сообщения.

        :return: набор текстов сообщений / изображений.
        """
        msg_text = "\n".join(i.strip() for i in msg_text.split("\n"))
        while "\n\n" in msg_text:
            msg_text = msg_text.replace("\n\n", "\n[a][/a]\n")

        pos = 0
        entities = []
        while entity := cardinal_tools.ENTITY_RE.search(msg_text, pos=pos):
            if text := msg_text[pos:entity.span()[0]].strip():
                entities.extend(self.split_text(text))

            variable = msg_text[entity.span()[0]:entity.span()[1]]
            if variable.startswith("$photo"):
                entities.append(int(variable.split("=")[1]))
            elif variable.startswith("$sleep"):
                entities.append(float(variable.split("=")[1]))
            pos = entity.span()[1]
        else:
            if text := msg_text[pos:].strip():
                entities.extend(self.split_text(text))
        return entities

    def send_message(self, chat_id: int | str, message_text: str, chat_name: str | None = None,
                     interlocutor_id: int | None = None, attempts: int = 3,
                     watermark: bool = True) -> list[FunPayAPI.types.Message] | None:
        """
        Отправляет сообщение в чат FunPay.

        :param chat_id: ID чата.
        :param message_text: текст сообщения.
        :param chat_name: название чата (необязательно).
        :param interlocutor_id: ID собеседника (необязательно).
        :param attempts: кол-во попыток на отправку сообщения.
        :param watermark: добавлять ли водяной знак в начало сообщения?

        :return: объект сообщения / последнего сообщения, если оно доставлено, иначе - None
        """
        if self.MAIN_CFG["Other"].get("watermark") and watermark and not message_text.strip().startswith("$photo="):
            message_text = f"{self.MAIN_CFG['Other']['watermark']}\n" + message_text

        entities = self.parse_message_entities(message_text)
        if all(isinstance(i, float) for i in entities) or not entities:
            return

        result = []
        for entity in entities:
            current_attempts = attempts
            while current_attempts:
                try:
                    if isinstance(entity, str):
                        msg = self.account.send_message(chat_id, entity, chat_name,
                                                        interlocutor_id or self.account.interlocutor_ids.get(chat_id),
                                                        None, not self.old_mode_enabled,
                                                        self.old_mode_enabled,
                                                        self.keep_sent_messages_unread)
                        result.append(msg)
                        logger.info(_("crd_msg_sent", chat_id))
                    elif isinstance(entity, int):
                        msg = self.account.send_image(chat_id, entity, chat_name,
                                                      interlocutor_id or self.account.interlocutor_ids.get(chat_id),
                                                      not self.old_mode_enabled,
                                                      self.old_mode_enabled,
                                                      self.keep_sent_messages_unread)
                        result.append(msg)
                        logger.info(_("crd_msg_sent", chat_id))
                    elif isinstance(entity, float):
                        time.sleep(entity)
                    break
                except Exception as ex:
                    logger.warning(_("crd_msg_send_err", chat_id))
                    logger.debug("TRACEBACK", exc_info=True)
                    logger.info(_("crd_msg_attempts_left", current_attempts))
                    current_attempts -= 1
                    time.sleep(1)
            else:
                logger.error(_("crd_msg_no_more_attempts_err", chat_id))
                return []
        return result

    def get_exchange_rate(self, base_currency: types.Currency, target_currency: types.Currency, min_interval: int = 60):
        """
        Получает курс обмена между двумя указанными валютами.
        Если с последней проверки прошло меньше `min_interval` секунд, используется сохранённое значение.

        :param base_currency: Исходная валюта, из которой производится обмен.
        :type base_currency: :obj:`types.Currency`

        :param target_currency: Целевая валюта, в которую производится обмен.
        :type target_currency: :obj:`types.Currency`

        :param min_interval: Минимальное время в секундах между проверками курса обмена.
        :type min_interval: :obj:`int`

        :return: Коэффициент обмена, где 1 единица `base_currency` = X единиц `target_currency`.
        :rtype: :obj:`float`
        """
        assert base_currency != types.Currency.UNKNOWN and target_currency != types.Currency.UNKNOWN
        if base_currency == target_currency:
            return 1.0 # Возвращаем float для консистентности
            
        # Проверяем кэш сначала для прямого курса, потом для обратного
        cached_rate, cache_time = self.__exchange_rates.get((base_currency, target_currency), (None, 0))
        if cached_rate is not None and time.time() < cache_time + min_interval:
            return cached_rate
        
        cached_rate_reverse, cache_time_reverse = self.__exchange_rates.get((target_currency, base_currency), (None, 0))
        if cached_rate_reverse is not None and time.time() < cache_time_reverse + min_interval:
            return 1.0 / cached_rate_reverse


        # Если в кэше нет или устарело, запрашиваем
        for attempt in range(3): # 3 попытки
            try:
                # Получаем курс относительно текущей валюты аккаунта до base_currency
                rate_to_base, actual_acc_currency_after_base_req = self.account.get_exchange_rate(base_currency)
                # Сохраняем оба курса (прямой и обратный)
                current_time = time.time()
                self.__exchange_rates[(actual_acc_currency_after_base_req, base_currency)] = (rate_to_base, current_time)
                if rate_to_base != 0: self.__exchange_rates[(base_currency, actual_acc_currency_after_base_req)] = (1.0 / rate_to_base, current_time)

                time.sleep(random.uniform(0.5, 1.0)) # Небольшая задержка

                # Получаем курс относительно текущей валюты аккаунта (которая могла измениться) до target_currency
                rate_to_target, actual_acc_currency_after_target_req = self.account.get_exchange_rate(target_currency)
                current_time = time.time()
                self.__exchange_rates[(actual_acc_currency_after_target_req, target_currency)] = (rate_to_target, current_time)
                if rate_to_target != 0: self.__exchange_rates[(target_currency, actual_acc_currency_after_target_req)] = (1.0 / rate_to_target, current_time)

                # Теперь нам нужно убедиться, что обе "базовые" валюты (actual_acc_currency_...) одинаковы
                # или мы можем их привести к одной.
                # Самый простой случай: если self.account.currency теперь совпадает с actual_acc_currency_after_base_req
                # и также с actual_acc_currency_after_target_req (т.е. валюта аккаунта не менялась или вернулась к одной и той же)
                
                # Если валюта аккаунта после первого запроса стала base_currency
                if actual_acc_currency_after_base_req == base_currency:
                    # Значит rate_to_base был 1.0 (или очень близок).
                    # Теперь self.account.currency == base_currency.
                    # Мы запрашиваем курс из base_currency в target_currency.
                    # rate_to_target - это и есть наш искомый курс base->target.
                    final_rate = rate_to_target
                    self.__exchange_rates[(base_currency, target_currency)] = (final_rate, time.time())
                    if final_rate != 0: self.__exchange_rates[(target_currency, base_currency)] = (1.0 / final_rate, time.time())
                    return final_rate
                
                # Если валюта аккаунта после второго запроса стала target_currency
                elif actual_acc_currency_after_target_req == target_currency:
                    # rate_to_target был 1.0
                    # self.account.currency == target_currency
                    # rate_to_base был курсом из target_currency в base_currency, т.е. target->base
                    # Нам нужен base->target, значит 1.0 / rate_to_base
                    final_rate = 1.0 / rate_to_base if rate_to_base != 0 else float('inf') # Защита от деления на ноль
                    self.__exchange_rates[(base_currency, target_currency)] = (final_rate, time.time())
                    if final_rate != 0 and final_rate != float('inf'): self.__exchange_rates[(target_currency, base_currency)] = (1.0 / final_rate, time.time())
                    return final_rate

                # Более сложный случай: если валюта аккаунта после обоих запросов одна и та же, но не base и не target
                # Например, RUB. Мы получили RUB->base и RUB->target. Тогда base->target = (RUB->target) / (RUB->base)
                if actual_acc_currency_after_base_req == actual_acc_currency_after_target_req:
                    # rate_to_base это курс ACC_CUR -> base_currency (сколько base_currency за 1 ACC_CUR)
                    # rate_to_target это курс ACC_CUR -> target_currency (сколько target_currency за 1 ACC_CUR)
                    # Нам нужен курс base_currency -> target_currency
                    # 1 base_currency = (1 / rate_to_base) ACC_CUR
                    # Это количество ACC_CUR даст (1 / rate_to_base) * rate_to_target единиц target_currency
                    if rate_to_base == 0: # Предотвращаем деление на ноль
                        logger.error("Нулевой курс обмена при расчете, невозможно определить курс.")
                        return float('inf') # или другое значение ошибки
                    final_rate = rate_to_target / rate_to_base
                    self.__exchange_rates[(base_currency, target_currency)] = (final_rate, time.time())
                    if final_rate != 0 and final_rate != float('inf'): self.__exchange_rates[(target_currency, base_currency)] = (1.0 / final_rate, time.time())
                    return final_rate

                logger.warning("Не удалось однозначно определить курс обмена из-за смены валюты аккаунта. Повторная попытка...")
                # Если валюта аккаунта менялась непредсказуемо, пробуем еще раз

            except Exception as e:
                logger.warning(f"Ошибка при получении курса обмена (попытка {attempt + 1}): {e}")
                if attempt < 2: time.sleep(random.uniform(1, 2)) # Пауза перед повтором
        
        logger.error("Не удалось получить курс обмена после нескольких попыток.")
        raise Exception("Не удалось получить курс обмена: превышено количество попыток.")

    def update_session(self, attempts: int = 3) -> bool:
        """
        Обновляет данные аккаунта (баланс, токены и т.д.)

        :param attempts: кол-во попыток.

        :return: True, если удалось обновить данные, False - если нет.
        """
        while attempts:
            try:
                self.account.get(update_phpsessid=True)
                logger.info(_("crd_session_updated"))
                return True
            except TimeoutError:
                logger.warning(_("crd_session_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str()) # Используем short_str()
                logger.debug(e)
            except:
                logger.error(_("crd_session_unexpected_err"))
                logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            if attempts > 0: # Выводим, только если будут еще попытки
                 logger.warning(_("crd_try_again_in_n_secs", 2))
                 time.sleep(2)
        else:
            logger.error(_("crd_session_no_more_attempts_err"))
            return False

    # Бесконечные циклы
    def process_events(self):
        """
        Запускает хэндлеры, привязанные к тому или иному событию.
        """
        instance_id = self.run_id
        events_handlers = {
            FunPayAPI.events.EventTypes.INITIAL_CHAT: self.init_message_handlers,
            FunPayAPI.events.EventTypes.CHATS_LIST_CHANGED: self.messages_list_changed_handlers,
            FunPayAPI.events.EventTypes.LAST_CHAT_MESSAGE_CHANGED: self.last_chat_message_changed_handlers,
            FunPayAPI.events.EventTypes.NEW_MESSAGE: self.new_message_handlers,

            FunPayAPI.events.EventTypes.INITIAL_ORDER: self.init_order_handlers,
            FunPayAPI.events.EventTypes.ORDERS_LIST_CHANGED: self.orders_list_changed_handlers,
            FunPayAPI.events.EventTypes.NEW_ORDER: self.new_order_handlers,
            FunPayAPI.events.EventTypes.ORDER_STATUS_CHANGED: self.order_status_changed_handlers,
        }

        for event in self.runner.listen(requests_delay=int(self.MAIN_CFG["Other"]["requestsDelay"])):
            if instance_id != self.run_id:
                break
            self.run_handlers(events_handlers[event.type], (self, event))

    def lots_raise_loop(self):
        """
        Запускает бесконечный цикл поднятия категорий (если autoRaise в _main.cfg == 1)
        """
        if not self.profile or not self.profile.get_lots(): # Добавил проверку на self.profile
            logger.info(_("crd_raise_loop_not_started"))
            return

        logger.info(_("crd_raise_loop_started"))
        while True:
            try:
                if not self.MAIN_CFG["FunPay"].getboolean("autoRaise"):
                    time.sleep(10)
                    continue
                next_time = self.raise_lots()
                delay = next_time - int(time.time())
                if delay <= 0: # Если время уже прошло или равно 0, поднимаем сразу (или с небольшой задержкой)
                    logger.debug(f"Небольшая задержка перед следующим поднятием (delay={delay}).")
                    time.sleep(random.uniform(1,3)) # Небольшая случайная задержка
                    continue
                logger.debug(f"Следующее поднятие лотов через: {cardinal_tools.time_to_str(delay)}")
                time.sleep(delay)
            except Exception as e: # Ловим общие исключения в цикле
                logger.error(f"Ошибка в цикле поднятия лотов: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(60) # Пауза в случае ошибки

    def update_session_loop(self):
        """
        Запускает бесконечный цикл обновления данных о пользователе.
        """
        logger.info(_("crd_session_loop_started"))
        default_sleep_time = 3600 # 1 час
        error_sleep_time = 60 # 1 минута в случае ошибки
        
        while True:
            time.sleep(default_sleep_time) # Сначала ждем
            result = self.update_session()
            # Логика изменения времени сна не нужна, так как update_session() сама делает попытки.
            # Если она не удалась, значит были серьезные проблемы, и через час снова попробуем.
            # Если нужно чаще при ошибке, то можно добавить:
            # sleep_time = error_sleep_time if not result else default_sleep_time

    # Управление процессом
    def init(self):
        """
        Инициализирует кортекс: регистрирует хэндлеры, инициализирует и запускает Telegram бота,
        получает данные аккаунта и профиля.
        """
        self.add_handlers_from_plugin(handlers)
        self.add_handlers_from_plugin(announcements) # Re-enabled
        self.load_plugins()
        self.add_handlers()

        if self.MAIN_CFG["Telegram"].getboolean("enabled"):
            self.__init_telegram()
            for module in [auto_response_cp, auto_delivery_cp, config_loader_cp, templates_cp, plugins_cp,
                           file_uploader, authorized_users_cp, proxy_cp, default_cp]:
                self.add_handlers_from_plugin(module)

        self.run_handlers(self.pre_init_handlers, (self,))

        if self.MAIN_CFG["Telegram"].getboolean("enabled"):
            self.telegram.setup_commands()
            try:
                self.telegram.edit_bot()
            except AttributeError:
                logger.warning("Произошла ошибка при изменении бота Telegram. Обновляю библиотеку pyTelegramBotAPI...")
                logger.debug("TRACEBACK", exc_info=True)
                try:
                    main(["install", "-U", "pytelegrambotapi>=4.15.2"]) # Версия как в requirements
                    logger.info("Библиотека pyTelegramBotAPI обновлена.")
                except:
                    logger.warning("Произошла ошибка при обновлении библиотеки pyTelegramBotAPI.")
                    logger.debug("TRACEBACK", exc_info=True)
            except Exception as e:
                logger.warning(f"Произошла ошибка при изменении информации о боте Telegram: {e}.")
                logger.debug("TRACEBACK", exc_info=True)

            Thread(target=self.telegram.run, daemon=True).start()

        self.__init_account()
        self.runner = FunPayAPI.Runner(self.account, self.old_mode_enabled)
        self.__update_profile()
        self.run_handlers(self.post_init_handlers, (self,))
        return self

    def run(self):
        """
        Запускает кортекс после инициализации. Используется для первого старта.
        """
        self.run_id += 1
        self.start_time = int(time.time())
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))

        Thread(target=self.lots_raise_loop, daemon=True).start()
        Thread(target=self.update_session_loop, daemon=True).start()
        self.process_events()

    def start(self):
        """
        Запускает кортекс после остановки. Не используется.
        """
        self.run_id += 1
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))
        self.process_events()

    def stop(self):
        """
        Останавливает кортекс. Не используется.
        """
        self.run_id += 1
        self.run_handlers(self.pre_stop_handlers, (self,))
        self.run_handlers(self.post_stop_handlers, (self,))

    def update_lots_and_categories(self):
        """
        Парсит лоты (для ПУ TG).
        """
        result = self.__update_profile(infinite_polling=False, attempts=3, update_main_profile=False)
        return result

    def switch_msg_get_mode(self):
        self.MAIN_CFG["FunPay"]["oldMsgGetMode"] = str(int(not self.old_mode_enabled))
        self.save_config(self.MAIN_CFG, "configs/_main.cfg")
        if not self.runner:
            return
        if not self.old_mode_enabled:
            self.runner.last_messages_ids = {k: v[0] for k, v in self.runner.runner_last_messages.items()}
        self.runner.make_msg_requests = False if self.old_mode_enabled else True
        if self.old_mode_enabled:
            self.runner.last_messages_ids = {}
            self.runner.by_bot_ids = {}

    @staticmethod
    def save_config(config: configparser.ConfigParser, file_path: str) -> None:
        """
        Сохраняет конфиг в указанный файл.

        :param config: объект конфига.
        :param file_path: путь до файла, в который нужно сохранить конфиг.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфига {file_path}: {e}")

    # Загрузка плагинов
    @staticmethod
    def is_uuid_valid(uuid_str: str) -> bool: # Renamed var
        """
        Проверяет, является ли UUID плагина валидным.
        :param uuid_str: UUID4 в виде строки.
        """
        try:
            uuid_obj = UUID(uuid_str, version=4)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_str.lower() # UUID обычно в нижнем регистре

    @staticmethod
    def is_plugin(file_path: str) -> bool: # Changed param to full path
        """
        Проверяет, является ли файл плагином (не содержит ли "# noplug" в первой строке).
        :param file_path: полный путь до файла плагина.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line.startswith("#") and "noplug" in first_line.split():
                return False
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке файла плагина {file_path}: {e}")
            return False # Считаем не плагином при ошибке чтения

    @staticmethod
    def load_plugin(plugin_file_name: str) -> tuple[ModuleType, dict] | None: # Renamed param, returns None on error
        """
        Создает модуль из переданного файла-плагина и получает необходимые поля для PluginData.
        :param plugin_file_name: имя файла-плагина (например, "my_plugin.py").
        :return: (модуль плагина, словарь с полями) или None при ошибке.
        """
        full_plugin_path = os.path.join("plugins", plugin_file_name)
        module_name = f"plugins.{plugin_file_name[:-3]}" # Убираем .py для имени модуля
        try:
            spec = importlib.util.spec_from_file_location(module_name, full_plugin_path)
            if spec is None or spec.loader is None: # Проверка на случай если spec не создался
                 logger.error(f"Не удалось создать spec для плагина {plugin_file_name}")
                 return None
            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = plugin_module # Регистрируем модуль
            spec.loader.exec_module(plugin_module)

            required_fields = ["NAME", "VERSION", "DESCRIPTION", "CREDITS", "UUID"]
            optional_fields = {"SETTINGS_PAGE": False, "BIND_TO_DELETE": None} # Значения по умолчанию
            
            plugin_data_dict = {}

            for field_name in required_fields:
                if not hasattr(plugin_module, field_name):
                    raise Utils.exceptions.FieldNotExistsError(field_name, plugin_file_name)
                plugin_data_dict[field_name] = getattr(plugin_module, field_name)
            
            for field_name, default_value in optional_fields.items():
                plugin_data_dict[field_name] = getattr(plugin_module, field_name, default_value)

            # Проверка UUID
            if not Cortex.is_uuid_valid(plugin_data_dict["UUID"]): # Вызываем статический метод
                 logger.error(_("crd_invalid_uuid", plugin_file_name)) # Используем существующий ключ локализации
                 return None


            return plugin_module, plugin_data_dict
        except Utils.exceptions.FieldNotExistsError as e: # Ловим свое же исключение
            logger.error(f"Ошибка загрузки плагина {plugin_file_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке плагина {plugin_file_name}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            return None


    def load_plugins(self):
        """
        Импортирует все плагины из папки plugins.
        """
        plugins_dir = "plugins"
        if not os.path.exists(plugins_dir):
            logger.warning(_("crd_no_plugins_folder"))
            return
        
        potential_plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"]
        if not potential_plugin_files:
            logger.info(_("crd_no_plugins"))
            return

        # Не нужно добавлять 'plugins' в sys.path если используем spec_from_file_location с полным путем
        # sys.path.append(plugins_dir) 

        for plugin_filename in potential_plugin_files:
            full_path = os.path.join(plugins_dir, plugin_filename)
            if not self.is_plugin(full_path): # Проверяем # noplug
                logger.info(f"Файл '{plugin_filename}' помечен как 'noplug', пропускается.")
                continue

            load_result = self.load_plugin(plugin_filename)
            if load_result is None:
                # Сообщение об ошибке уже было выведено в load_plugin
                continue 
            
            plugin_module, plugin_fields_dict = load_result

            plugin_uuid = plugin_fields_dict["UUID"]
            if plugin_uuid in self.plugins:
                logger.error(_("crd_uuid_already_registered", plugin_uuid, plugin_fields_dict['NAME']))
                continue

            is_enabled = plugin_uuid not in self.disabled_plugins
            
            plugin_data_instance = PluginData(
                name=plugin_fields_dict["NAME"],
                version=plugin_fields_dict["VERSION"],
                desc=plugin_fields_dict["DESCRIPTION"],
                credentials=plugin_fields_dict["CREDITS"],
                uuid=plugin_uuid,
                path=full_path, # Сохраняем полный путь
                plugin=plugin_module,
                settings_page=plugin_fields_dict["SETTINGS_PAGE"],
                delete_handler=plugin_fields_dict["BIND_TO_DELETE"],
                enabled=is_enabled
            )
            self.plugins[plugin_uuid] = plugin_data_instance
            logger.info(f"Плагин '{plugin_data_instance.name}' v{plugin_data_instance.version} (UUID: {plugin_uuid}) успешно загружен. Статус: {'Включен' if is_enabled else 'Выключен'}.")


    def add_handlers_from_plugin(self, plugin, uuid: str | None = None):
        """
        Добавляет хэндлеры из плагина + присваивает каждому хэндлеру UUID плагина.

        :param plugin: модуль (плагин).
        :param uuid: UUID плагина (None для встроенных хэндлеров).
        """
        for name in self.handler_bind_var_names:
            try:
                functions = getattr(plugin, name)
            except AttributeError:
                continue
            for func in functions:
                func.plugin_uuid = uuid
            self.handler_bind_var_names[name].extend(functions)
        logger.info(_("crd_handlers_registered", plugin.__name__))

    def add_handlers(self):
        """
        Регистрирует хэндлеры из всех плагинов.
        """
        for i in self.plugins:
            plugin = self.plugins[i].plugin
            self.add_handlers_from_plugin(plugin, i)

    def run_handlers(self, handlers_list: list[Callable], args) -> None:
        """
        Выполняет функции из списка handlers.

        :param handlers_list: Список хэндлеров.
        :param args: аргументы для хэндлеров.
        """
        for func in handlers_list:
            try:
                # Проверяем, что плагин, к которому привязан хендлер, существует и включен,
                # или это системный хендлер (plugin_uuid is None)
                plugin_uuid_attr = getattr(func, "plugin_uuid", None)
                if plugin_uuid_attr is None or \
                   (plugin_uuid_attr in self.plugins and self.plugins[plugin_uuid_attr].enabled):
                    func(*args)
            except Exception as ex:
                error_message_short = ""
                if hasattr(ex, 'short_str') and callable(getattr(ex, 'short_str')):
                    error_message_short = f" ({ex.short_str()})" # Добавляем скобки для ясности
                
                # crd_handler_err уже локализован
                logger.error(_("crd_handler_err") + error_message_short)
                logger.debug("TRACEBACK", exc_info=True)
                continue


    def add_telegram_commands(self, uuid: str, commands: list[tuple[str, str, bool]]):
        """
        Добавляет команды в список команд плагина.
        [
            ("команда1", "описание команды", Добавлять ли в меню команд (True / False)),
            ("команда2", "описание команды", Добавлять ли в меню команд (True / False))
        ]

        :param uuid: UUID плагина.
        :param commands: список команд (без "/")
        """
        if uuid not in self.plugins:
            logger.warning(f"Попытка добавить команды для несуществующего плагина UUID: {uuid}")
            return

        plugin_obj = self.plugins[uuid]
        for command_text, help_text_key, add_to_menu_flag in commands:
            plugin_obj.commands[command_text] = help_text_key # Сохраняем ключ для локализации
            if add_to_menu_flag and self.telegram:
                # Описание команды будет локализовано в TGBot.setup_commands
                self.telegram.add_command_to_menu(command_text, help_text_key)
        logger.info(f"Команды для плагина '{plugin_obj.name}' (UUID: {uuid}) зарегистрированы в Telegram.")


    def toggle_plugin(self, uuid):
        """
        Активирует / деактивирует плагин.
        :param uuid: UUID плагина.
        """
        if uuid not in self.plugins:
            logger.warning(f"Попытка переключить несуществующий плагин UUID: {uuid}")
            return

        self.plugins[uuid].enabled = not self.plugins[uuid].enabled
        if self.plugins[uuid].enabled and uuid in self.disabled_plugins:
            self.disabled_plugins.remove(uuid)
        elif not self.plugins[uuid].enabled and uuid not in self.disabled_plugins:
            self.disabled_plugins.append(uuid)
        cardinal_tools.cache_disabled_plugins(self.disabled_plugins)
        logger.info(f"Плагин '{self.plugins[uuid].name}' (UUID: {uuid}) теперь {'включен' if self.plugins[uuid].enabled else 'выключен'}.")


    # Настройки (без изменений)
    @property
    def autoraise_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoRaise")

    @property
    def autoresponse_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoResponse")

    @property
    def autodelivery_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoDelivery")

    @property
    def multidelivery_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("multiDelivery")

    @property
    def autorestore_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoRestore")

    @property
    def autodisable_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("autoDisable")

    @property
    def old_mode_enabled(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("oldMsgGetMode")

    @property
    def keep_sent_messages_unread(self) -> bool:
        return self.MAIN_CFG["FunPay"].getboolean("keepSentMessagesUnread")

    @property
    def show_image_name(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("showImageName")

    @property
    def bl_delivery_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockDelivery")

    @property
    def bl_response_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockResponse")

    @property
    def bl_msg_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockNewMessageNotification")

    @property
    def bl_order_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockNewOrderNotification")

    @property
    def bl_cmd_notification_enabled(self) -> bool:
        return self.MAIN_CFG["BlockList"].getboolean("blockCommandNotification")

    @property
    def include_my_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeMyMessages")

    @property
    def include_fp_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeFPMessages")

    @property
    def include_bot_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("includeBotMessages")

    @property
    def only_my_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyMyMessages")

    @property
    def only_fp_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyFPMessages")

    @property
    def only_bot_msg_enabled(self) -> bool:
        return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyBotMessages")

    @property
    def block_tg_login(self) -> bool:
        return self.MAIN_CFG["Telegram"].getboolean("blockLogin")

# END OF FILE FunPayCortex/cortex.py