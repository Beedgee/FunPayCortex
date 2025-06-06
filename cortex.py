# START OF FILE FunPayCortex/cortex.py

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
import announcements
from locales.localizer import Localizer
from FunPayAPI import utils as fp_utils
from Utils import cortex_tools
import tg_bot.bot

from threading import Thread

logger = logging.getLogger("FPC")
localizer = Localizer()
_ = localizer.translate


def get_cortex() -> None | Cortex:
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


class Cortex(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Cortex, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self, main_config: ConfigParser,
                 auto_delivery_config: ConfigParser,
                 auto_response_config: ConfigParser,
                 raw_auto_response_config: ConfigParser,
                 version: str):
        self.VERSION = version
        self.instance_id = random.randint(0, 999999999)
        self.delivery_tests = {}

        self.MAIN_CFG = main_config
        self.AD_CFG = auto_delivery_config
        self.AR_CFG = auto_response_config
        self.RAW_AR_CFG = raw_auto_response_config
        self.proxy = {}
        self.proxy_dict = cortex_tools.load_proxy_dict()
        if self.MAIN_CFG["Proxy"].getboolean("enable"):
            if self.MAIN_CFG["Proxy"]["ip"] and self.MAIN_CFG["Proxy"]["port"].isnumeric():
                logger.info(_("crd_proxy_detected"))
                ip, port = self.MAIN_CFG["Proxy"]["ip"], self.MAIN_CFG["Proxy"]["port"]
                login, password = self.MAIN_CFG["Proxy"]["login"], self.MAIN_CFG["Proxy"]["password"]
                proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
                self.proxy = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
                if proxy_str not in self.proxy_dict.values():
                    max_id = max(self.proxy_dict.keys(), default=-1)
                    self.proxy_dict[max_id + 1] = proxy_str
                    cortex_tools.cache_proxy_dict(self.proxy_dict)
                if self.MAIN_CFG["Proxy"].getboolean("check") and not cortex_tools.check_proxy(self.proxy):
                    sys.exit()

        self.account = FunPayAPI.Account(self.MAIN_CFG["FunPay"]["golden_key"],
                                         self.MAIN_CFG["FunPay"]["user_agent"],
                                         proxy=self.proxy,
                                         locale=self.MAIN_CFG["FunPay"].get("locale", "ru"))
        self.runner: FunPayAPI.Runner | None = None
        self.telegram: tg_bot.bot.TGBot | None = None
        self.running = False
        self.run_id = 0
        self.start_time = int(time.time())
        self.balance: FunPayAPI.types.Balance | None = None
        self.raise_time = {}
        self.raised_time = {}
        self.__exchange_rates = {}
        self.profile: FunPayAPI.types.UserProfile | None = None
        self.tg_profile: FunPayAPI.types.UserProfile | None = None
        self.last_tg_profile_update = datetime.datetime.now()
        self.curr_profile: FunPayAPI.types.UserProfile | None = None
        self.curr_profile_last_tag: str | None = None
        self.profile_last_tag: str | None = None
        self.last_state_change_tag: str | None = None
        self.blacklist = cortex_tools.load_blacklist()
        self.old_users = cortex_tools.load_old_users(
            float(self.MAIN_CFG["Greetings"]["greetingsCooldown"]))

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
            "BIND_TO_PRE_INIT": self.pre_init_handlers, "BIND_TO_POST_INIT": self.post_init_handlers,
            "BIND_TO_PRE_START": self.pre_start_handlers, "BIND_TO_POST_START": self.post_start_handlers,
            "BIND_TO_PRE_STOP": self.pre_stop_handlers, "BIND_TO_POST_STOP": self.post_stop_handlers,
            "BIND_TO_INIT_MESSAGE": self.init_message_handlers,
            "BIND_TO_MESSAGES_LIST_CHANGED": self.messages_list_changed_handlers,
            "BIND_TO_LAST_CHAT_MESSAGE_CHANGED": self.last_chat_message_changed_handlers,
            "BIND_TO_NEW_MESSAGE": self.new_message_handlers, "BIND_TO_INIT_ORDER": self.init_order_handlers,
            "BIND_TO_NEW_ORDER": self.new_order_handlers,
            "BIND_TO_ORDERS_LIST_CHANGED": self.orders_list_changed_handlers,
            "BIND_TO_ORDER_STATUS_CHANGED": self.order_status_changed_handlers,
            "BIND_TO_PRE_DELIVERY": self.pre_delivery_handlers, "BIND_TO_POST_DELIVERY": self.post_delivery_handlers,
            "BIND_TO_PRE_LOTS_RAISE": self.pre_lots_raise_handlers,
            "BIND_TO_POST_LOTS_RAISE": self.post_lots_raise_handlers,
        }
        self.plugins: dict[str, PluginData] = {}
        self.disabled_plugins = cortex_tools.load_disabled_plugins()

    def __init_account(self) -> None:
        while True:
            try:
                self.account.get()
                self.balance = self.get_balance()
                greeting_text = cortex_tools.create_greeting_text(self)
                cortex_tools.set_console_title(f"FunPay Cortex - {self.account.username} ({self.account.id})")
                for line in greeting_text.split("\n"):
                    logger.info(line)
                break
            except TimeoutError:
                logger.error(_("crd_acc_get_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str())
                logger.debug(f"TRACEBACK {e.short_str()}", exc_info=True)
            except Exception as e:
                logger.error(_("crd_acc_get_unexpected_err") + f": {e}")
                logger.debug("TRACEBACK", exc_info=True)
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)

    def __update_profile(self, infinite_polling: bool = True, attempts: int = 0, update_telegram_profile: bool = True,
                         update_main_profile: bool = True) -> bool:
        logger.info(_("crd_getting_profile_data"))
        current_attempts = 0
        max_attempts = attempts if not infinite_polling else float('inf')
        profile = None
        while current_attempts < max_attempts:
            try:
                profile = self.account.get_user(self.account.id)
                break
            except TimeoutError:
                logger.error(_("crd_profile_get_timeout_err"))
            except FunPayAPI.exceptions.RequestFailedError as e:
                logger.error(e.short_str())
                logger.debug("TRACEBACK", exc_info=True)
            except Exception as e:
                logger.error(_("crd_profile_get_unexpected_err") + f": {e}")
                logger.debug("TRACEBACK", exc_info=True)
            current_attempts += 1
            if current_attempts >= max_attempts and not infinite_polling:
                 logger.error(_("crd_profile_get_too_many_attempts_err", attempts))
                 return False
            logger.warning(_("crd_try_again_in_n_secs", 2))
            time.sleep(2)
        else:
            if not infinite_polling:
                logger.error(_("crd_profile_get_too_many_attempts_err", attempts))
                return False
            logger.critical("Критическая ошибка в логике __update_profile с infinite_polling.")
            return False

        if profile is None:
            logger.error("Не удалось получить профиль пользователя после всех попыток в __update_profile.")
            return False

        if update_main_profile:
            self.profile = profile
            self.curr_profile = profile
            logger.info(_("crd_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        if update_telegram_profile:
            self.tg_profile = profile
            self.last_tg_profile_update = datetime.datetime.now()
            logger.info(_("crd_tg_profile_updated", len(profile.get_lots()), len(profile.get_sorted_lots(2))))
        return True

    def __init_telegram(self) -> None:
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
                 logger.debug("TRACEBACK", exc_info=True)
                 time.sleep(1)
            current_attempts +=1
        if not lots:
             raise Exception(f"Не удалось найти публичные лоты для определения баланса после {attempts} попыток.")
        balance = self.account.get_balance(random.choice(lots).id)
        return balance

    def raise_lots(self) -> int:
        next_call = float("inf")
        unique_categories = []
        seen_category_ids = set()
        if not self.profile or not self.profile.get_lots():
            logger.info("Нет лотов в профиле для поднятия. Пропуск цикла поднятия.")
            return 300

        for subcat_obj in self.profile.get_sorted_lots(2).keys():
            if subcat_obj.category.id not in seen_category_ids:
                unique_categories.append(subcat_obj.category)
                seen_category_ids.add(subcat_obj.category.id)
        sorted_categories_to_raise = sorted(unique_categories, key=lambda cat: cat.position)

        for category_obj in sorted_categories_to_raise:
            if (saved_raise_time := self.raise_time.get(category_obj.id)) and saved_raise_time > int(time.time()):
                next_call = min(next_call, saved_raise_time)
                continue

            active_common_subcategories_in_game = []
            for sub_category_obj_from_profile, lots_dict_in_subcategory in self.profile.get_sorted_lots(2).items():
                if sub_category_obj_from_profile.category.id == category_obj.id and \
                   sub_category_obj_from_profile.type == SubCategoryTypes.COMMON and \
                   lots_dict_in_subcategory:
                    active_common_subcategories_in_game.append(sub_category_obj_from_profile)
            unique_common_subcats = list(set(sc.id for sc in active_common_subcategories_in_game))

            if not unique_common_subcats:
                logger.debug(f"У категории '{category_obj.name}' нет активных COMMON лотов для поднятия, пропускаем.")
                self.raise_time[category_obj.id] = int(time.time()) + 7200
                next_call = min(next_call, self.raise_time[category_obj.id])
                continue

            raise_ok = False
            error_text_msg = ""
            time_delta_str = ""
            exception_occurred = None

            try:
                time.sleep(random.uniform(0.5, 1.5))
                self.account.raise_lots(category_obj.id, subcategories=unique_common_subcats)
                logger.info(_("crd_lots_raised", category_obj.name))
                raise_ok = True
                last_raised_timestamp = self.raised_time.get(category_obj.id)
                current_timestamp = int(time.time())
                self.raised_time[category_obj.id] = current_timestamp
                if last_raised_timestamp:
                    time_delta_str = f" Последнее поднятие: {cortex_tools.time_to_str(current_timestamp - last_raised_timestamp)} назад."
                next_raise_attempt_time = current_timestamp + 7200
                self.raise_time[category_obj.id] = next_raise_attempt_time
                next_call = min(next_call, next_raise_attempt_time)
            except FunPayAPI.exceptions.RaiseError as e:
                exception_occurred = e
                error_text_msg = e.error_message if e.error_message else "Неизвестная ошибка FunPay."
                wait_duration = e.wait_time if e.wait_time is not None else 60
                logger.warning(_("crd_raise_time_err", category_obj.name, error_text_msg, cortex_tools.time_to_str(wait_duration)))
                next_raise_attempt_time = int(time.time()) + wait_duration
                self.raise_time[category_obj.id] = next_raise_attempt_time
                next_call = min(next_call, next_raise_attempt_time)
            except Exception as e:
                exception_occurred = e
                default_retry_delay = 60
                error_log_message = _("crd_raise_unexpected_err", category_obj.name)
                if isinstance(e, FunPayAPI.exceptions.RequestFailedError) and e.status_code in (503, 403, 429):
                    error_log_message = _("crd_raise_status_code_err", e.status_code, category_obj.name)
                    default_retry_delay = 120
                logger.error(error_log_message)
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(random.uniform(default_retry_delay / 2, default_retry_delay))
                next_raise_attempt_time = int(time.time()) + 1
                next_call = min(next_call, next_raise_attempt_time)

            if raise_ok or isinstance(exception_occurred, FunPayAPI.exceptions.RaiseError):
                 self.run_handlers(self.post_lots_raise_handlers, (self, category_obj, error_text_msg + time_delta_str))
        return next_call if next_call < float("inf") else 300

    def get_order_from_object(self, obj: types.OrderShortcut | types.Message | types.ChatShortcut,
                              order_id_str: str | None = None) -> None | types.Order:
        if obj._order_attempt_error:
            return None
        if obj._order_attempt_made and obj._order is not None:
            return obj._order
        if obj._order_attempt_made and obj._order is None:
            wait_count = 0
            while obj._order is None and not obj._order_attempt_error and wait_count < 50:
                time.sleep(0.1)
                wait_count +=1
            return obj._order

        obj._order_attempt_made = True
        if not isinstance(obj, (types.Message, types.ChatShortcut, types.OrderShortcut)):
            obj._order_attempt_error = True
            logger.error(f"Неправильный тип объекта для get_order_from_object: {type(obj)}")
            return None

        final_order_id = order_id_str
        if not final_order_id:
            if isinstance(obj, types.OrderShortcut):
                final_order_id = obj.id
                if final_order_id == "ADTEST":
                    obj._order_attempt_error = True
                    return None
            elif isinstance(obj, (types.Message, types.ChatShortcut)):
                match = fp_utils.RegularExpressions().ORDER_ID.search(str(obj))
                if not match:
                    obj._order_attempt_error = True
                    return None
                final_order_id = match.group(0)[1:]
        if not final_order_id:
            obj._order_attempt_error = True
            return None

        for attempt_num in range(3, 0, -1):
            try:
                fetched_order = self.account.get_order(final_order_id)
                obj._order = fetched_order
                logger.info(f"Получена информация о заказе #{final_order_id}")
                return fetched_order
            except Exception as e:
                logger.warning(f"Ошибка при получении заказа #{final_order_id} (попытка {4-attempt_num}): {e}")
                logger.debug("TRACEBACK", exc_info=True)
                if attempt_num > 1: time.sleep(random.uniform(0.5, 1.5))
        obj._order_attempt_error = True
        return None

    @staticmethod
    def split_text(text: str) -> list[str]:
        output = []
        lines = text.split("\n")
        while lines:
            subtext = "\n".join(lines[:20])
            del lines[:20]
            if (strip := subtext.strip()) and strip != "[a][/a]":
                output.append(subtext)
        return output

    def parse_message_entities(self, msg_text: str) -> list[str | int | float]:
        msg_text = "\n".join(i.strip() for i in msg_text.split("\n"))
        while "\n\n" in msg_text:
            msg_text = msg_text.replace("\n\n", "\n[a][/a]\n")
        pos = 0
        entities = []
        while entity := cortex_tools.ENTITY_RE.search(msg_text, pos=pos):
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
        if self.MAIN_CFG["Other"].get("watermark") and watermark and not message_text.strip().startswith("$photo="):
            message_text = f"{self.MAIN_CFG['Other']['watermark']}\n" + message_text
        entities = self.parse_message_entities(message_text)
        if all(isinstance(i, float) for i in entities) or not entities:
            return None
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
                    logger.warning(_("crd_msg_send_err", chat_id) + f": {ex}")
                    logger.debug("TRACEBACK", exc_info=True)
                    logger.info(_("crd_msg_attempts_left", current_attempts))
                    current_attempts -= 1
                    time.sleep(1)
            else:
                logger.error(_("crd_msg_no_more_attempts_err", chat_id))
                return []
        return result

    def get_exchange_rate(self, base_currency: types.Currency, target_currency: types.Currency, min_interval: int = 60):
        assert base_currency != types.Currency.UNKNOWN and target_currency != types.Currency.UNKNOWN
        if base_currency == target_currency:
            return 1.0
        cached_rate, cache_time = self.__exchange_rates.get((base_currency, target_currency), (None, 0))
        if cached_rate is not None and time.time() < cache_time + min_interval:
            return cached_rate
        cached_rate_reverse, cache_time_reverse = self.__exchange_rates.get((target_currency, base_currency), (None, 0))
        if cached_rate_reverse is not None and time.time() < cache_time_reverse + min_interval:
            if cached_rate_reverse == 0:
                logger.error(f"Обратный курс для {target_currency.name} -> {base_currency.name} равен нулю. Невозможно рассчитать курс.")
                return float('inf')
            return 1.0 / cached_rate_reverse

        for attempt in range(3):
            try:
                rate_to_base, actual_acc_currency_after_base_req = self.account.get_exchange_rate(base_currency)
                current_time = time.time()
                self.__exchange_rates[(actual_acc_currency_after_base_req, base_currency)] = (rate_to_base, current_time)
                if rate_to_base != 0: self.__exchange_rates[(base_currency, actual_acc_currency_after_base_req)] = (1.0 / rate_to_base, current_time)
                time.sleep(random.uniform(0.5, 1.0))
                rate_to_target, actual_acc_currency_after_target_req = self.account.get_exchange_rate(target_currency)
                current_time = time.time()
                self.__exchange_rates[(actual_acc_currency_after_target_req, target_currency)] = (rate_to_target, current_time)
                if rate_to_target != 0: self.__exchange_rates[(target_currency, actual_acc_currency_after_target_req)] = (1.0 / rate_to_target, current_time)

                if actual_acc_currency_after_base_req == base_currency:
                    final_rate = rate_to_target
                elif actual_acc_currency_after_target_req == target_currency:
                    if rate_to_base == 0:
                        logger.error(f"Курс {actual_acc_currency_after_target_req.name} -> {base_currency.name} равен нулю. Невозможно рассчитать курс.")
                        final_rate = float('inf')
                    else:
                        final_rate = 1.0 / rate_to_base
                elif actual_acc_currency_after_base_req == actual_acc_currency_after_target_req:
                    if rate_to_base == 0:
                        logger.error(f"Курс {actual_acc_currency_after_base_req.name} -> {base_currency.name} равен нулю. Невозможно рассчитать курс.")
                        final_rate = float('inf')
                    else:
                        final_rate = rate_to_target / rate_to_base
                else:
                    logger.warning(f"Несовпадение валют аккаунта при расчете курса: {actual_acc_currency_after_base_req.name} vs {actual_acc_currency_after_target_req.name}. Попытка {attempt + 1}.")
                    if attempt < 2: continue
                    raise Exception("Не удалось определить курс из-за непредсказуемой смены валюты аккаунта.")


                self.__exchange_rates[(base_currency, target_currency)] = (final_rate, time.time())
                if final_rate != 0 and final_rate != float('inf'): self.__exchange_rates[(target_currency, base_currency)] = (1.0 / final_rate, time.time())
                return final_rate
            except Exception as e:
                logger.warning(f"Ошибка при получении курса обмена (попытка {attempt + 1}): {e}")
                logger.debug("TRACEBACK", exc_info=True)
                if attempt < 2: time.sleep(random.uniform(1, 2))
        logger.error("Не удалось получить курс обмена после нескольких попыток.")
        raise Exception("Не удалось получить курс обмена: превышено количество попыток.")

    def update_session(self, attempts: int = 3) -> bool:
        while attempts:
            try:
                self.account.get(update_phpsessid=True)
                logger.info(_("crd_session_updated"))
                return True
            except TimeoutError:
                logger.warning(_("crd_session_timeout_err"))
            except (FunPayAPI.exceptions.UnauthorizedError, FunPayAPI.exceptions.RequestFailedError) as e:
                logger.error(e.short_str())
                logger.debug("TRACEBACK", exc_info=True)
            except Exception as e:
                logger.error(_("crd_session_unexpected_err") + f": {e}")
                logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            if attempts > 0:
                 logger.warning(_("crd_try_again_in_n_secs", 2))
                 time.sleep(2)
        else:
            logger.error(_("crd_session_no_more_attempts_err"))
            return False

    def process_events(self):
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
        if not self.profile or not self.profile.get_lots():
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
                if delay <= 0:
                    logger.debug(f"Небольшая задержка перед следующим поднятием (delay={delay}).")
                    time.sleep(random.uniform(1,3))
                    continue
                logger.debug(f"Следующее поднятие лотов через: {cortex_tools.time_to_str(delay)}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Ошибка в цикле поднятия лотов: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(60)

    def update_session_loop(self):
        logger.info(_("crd_session_loop_started"))
        default_sleep_time = 3600
        while True:
            time.sleep(default_sleep_time)
            self.update_session()

    def init(self):
        self.add_handlers_from_plugin(handlers)
        self.add_handlers_from_plugin(announcements)
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
            except AttributeError as e:
                logger.warning("Произошла ошибка при изменении бота Telegram (AttributeError). Обновляю библиотеку pyTelegramBotAPI...")
                logger.debug(f"Details: {e}", exc_info=True)
                try:
                    main(["install", "-U", "pytelegrambotapi>=4.15.2"])
                    logger.info("Библиотека pyTelegramBotAPI обновлена.")
                except Exception as install_e:
                    logger.warning(f"Произошла ошибка при обновлении библиотеки pyTelegramBotAPI: {install_e}.")
                    logger.debug("TRACEBACK", exc_info=True)
            except Exception as e:
                logger.warning(f"Произошла ошибка при изменении информации о боте Telegram: {e}.")
                logger.debug("TRACEBACK", exc_info=True)
            Thread(target=self.telegram.run, daemon=True).start()
        self.__init_account()
        self.runner = FunPayAPI.Runner(self.account,
                                       disable_message_requests=self.old_mode_enabled,
                                       disabled_order_requests=False,
                                       disabled_buyer_viewing_requests=True)
        self.__update_profile()
        self.run_handlers(self.post_init_handlers, (self,))
        return self

    def run(self):
        self.run_id += 1
        self.start_time = int(time.time())
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))
        Thread(target=self.lots_raise_loop, daemon=True).start()
        Thread(target=self.update_session_loop, daemon=True).start()
        self.process_events()

    def start(self):
        self.run_id += 1
        self.run_handlers(self.pre_start_handlers, (self,))
        self.run_handlers(self.post_start_handlers, (self,))
        self.process_events()

    def stop(self):
        self.run_id += 1
        self.run_handlers(self.pre_stop_handlers, (self,))
        self.run_handlers(self.post_stop_handlers, (self,))

    def update_lots_and_categories(self):
        result = self.__update_profile(infinite_polling=False, attempts=3, update_main_profile=False)
        return result

    def switch_msg_get_mode(self):
        self.MAIN_CFG["FunPay"]["oldMsgGetMode"] = str(int(not self.old_mode_enabled))
        self.save_config(self.MAIN_CFG, "configs/_main.cfg")
        if not self.runner:
            return
        self.runner.make_msg_requests = not self.old_mode_enabled
        if self.old_mode_enabled:
            self.runner.last_messages_ids = {}
            self.runner.by_bot_ids = {}
        else:
            self.runner.last_messages_ids = {k: v[0] for k, v in self.runner.runner_last_messages.items()}


    @staticmethod
    def save_config(config: configparser.ConfigParser, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                config.write(f)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфига {file_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)

    @staticmethod
    def is_uuid_valid(uuid_str: str) -> bool:
        try:
            uuid_obj = UUID(uuid_str, version=4)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_str.lower()

    @staticmethod
    def is_plugin(file_path: str) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line.startswith("#") and "noplug" in first_line.split():
                return False
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке файла плагина {file_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            return False

    @staticmethod
    def load_plugin(plugin_file_name: str) -> tuple[ModuleType, dict] | None:
        full_plugin_path = os.path.join("plugins", plugin_file_name)
        module_name = f"plugins.{plugin_file_name[:-3]}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, full_plugin_path)
            if spec is None or spec.loader is None:
                 logger.error(f"Не удалось создать spec для плагина {plugin_file_name}")
                 return None
            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = plugin_module
            spec.loader.exec_module(plugin_module)
            required_fields = ["NAME", "VERSION", "DESCRIPTION", "CREDITS", "UUID"]
            optional_fields = {"SETTINGS_PAGE": False, "BIND_TO_DELETE": None}
            plugin_data_dict = {}
            for field_name in required_fields:
                if not hasattr(plugin_module, field_name):
                    raise Utils.exceptions.FieldNotExistsError(field_name, plugin_file_name)
                plugin_data_dict[field_name] = getattr(plugin_module, field_name)
            for field_name, default_value in optional_fields.items():
                plugin_data_dict[field_name] = getattr(plugin_module, field_name, default_value)
            if not Cortex.is_uuid_valid(plugin_data_dict["UUID"]):
                 logger.error(_("crd_invalid_uuid", plugin_file_name))
                 return None
            return plugin_module, plugin_data_dict
        except Utils.exceptions.FieldNotExistsError as e:
            logger.error(f"Ошибка загрузки плагина {plugin_file_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке плагина {plugin_file_name}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            return None

    def load_plugins(self):
        plugins_dir = "plugins"
        if not os.path.exists(plugins_dir):
            logger.warning(_("crd_no_plugins_folder"))
            return
        potential_plugin_files = [f for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"]
        if not potential_plugin_files:
            logger.info(_("crd_no_plugins"))
            return
        for plugin_filename in potential_plugin_files:
            full_path = os.path.join(plugins_dir, plugin_filename)
            if not self.is_plugin(full_path):
                logger.info(f"Файл '{plugin_filename}' помечен как 'noplug', пропускается.")
                continue
            load_result = self.load_plugin(plugin_filename)
            if load_result is None:
                continue
            plugin_module, plugin_fields_dict = load_result
            plugin_uuid = plugin_fields_dict["UUID"]
            if plugin_uuid in self.plugins:
                logger.error(_("crd_uuid_already_registered", plugin_uuid, plugin_fields_dict['NAME']))
                continue
            is_enabled = plugin_uuid not in self.disabled_plugins
            plugin_data_instance = PluginData(
                name=plugin_fields_dict["NAME"], version=plugin_fields_dict["VERSION"],
                desc=plugin_fields_dict["DESCRIPTION"], credentials=plugin_fields_dict["CREDITS"],
                uuid=plugin_uuid, path=full_path, plugin=plugin_module,
                settings_page=plugin_fields_dict["SETTINGS_PAGE"],
                delete_handler=plugin_fields_dict["BIND_TO_DELETE"], enabled=is_enabled
            )
            self.plugins[plugin_uuid] = plugin_data_instance
            logger.info(f"Плагин '{plugin_data_instance.name}' v{plugin_data_instance.version} (UUID: {plugin_uuid}) успешно загружен. Статус: {'Включен' if is_enabled else 'Выключен'}.")

    def add_handlers_from_plugin(self, plugin, uuid: str | None = None):
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
        for i in self.plugins:
            plugin = self.plugins[i].plugin
            self.add_handlers_from_plugin(plugin, i)

    def run_handlers(self, handlers_list: list[Callable], args) -> None:
        for func in handlers_list:
            try:
                plugin_uuid_attr = getattr(func, "plugin_uuid", None)
                if plugin_uuid_attr is None or \
                   (plugin_uuid_attr in self.plugins and self.plugins[plugin_uuid_attr].enabled):
                    func(*args)
            except Exception as ex:
                error_message_short = f" ({ex.short_str()})" if hasattr(ex, 'short_str') and callable(getattr(ex, 'short_str')) else ""
                logger.error(_("crd_handler_err") + error_message_short)
                logger.debug("TRACEBACK", exc_info=True)
                continue

    def add_telegram_commands(self, uuid: str, commands: list[tuple[str, str, bool]]):
        if uuid not in self.plugins:
            logger.warning(f"Попытка добавить команды для несуществующего плагина UUID: {uuid}")
            return
        plugin_obj = self.plugins[uuid]
        for command_text, help_text_key, add_to_menu_flag in commands:
            plugin_obj.commands[command_text] = help_text_key
            if add_to_menu_flag and self.telegram:
                self.telegram.add_command_to_menu(command_text, help_text_key)
        logger.info(f"Команды для плагина '{plugin_obj.name}' (UUID: {uuid}) зарегистрированы в Telegram.")

    def toggle_plugin(self, uuid):
        if uuid not in self.plugins:
            logger.warning(f"Попытка переключить несуществующий плагин UUID: {uuid}")
            return
        self.plugins[uuid].enabled = not self.plugins[uuid].enabled
        if self.plugins[uuid].enabled and uuid in self.disabled_plugins:
            self.disabled_plugins.remove(uuid)
        elif not self.plugins[uuid].enabled and uuid not in self.disabled_plugins:
            self.disabled_plugins.append(uuid)
        cortex_tools.cache_disabled_plugins(self.disabled_plugins)
        logger.info(f"Плагин '{self.plugins[uuid].name}' (UUID: {uuid}) теперь {'включен' if self.plugins[uuid].enabled else 'выключен'}.")

    @property
    def autoraise_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("autoRaise")
    @property
    def autoresponse_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("autoResponse")
    @property
    def autodelivery_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("autoDelivery")
    @property
    def multidelivery_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("multiDelivery")
    @property
    def autorestore_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("autoRestore")
    @property
    def autodisable_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("autoDisable")
    @property
    def old_mode_enabled(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("oldMsgGetMode")
    @property
    def keep_sent_messages_unread(self) -> bool: return self.MAIN_CFG["FunPay"].getboolean("keepSentMessagesUnread")
    @property
    def show_image_name(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("showImageName")
    @property
    def bl_delivery_enabled(self) -> bool: return self.MAIN_CFG["BlockList"].getboolean("blockDelivery")
    @property
    def bl_response_enabled(self) -> bool: return self.MAIN_CFG["BlockList"].getboolean("blockResponse")
    @property
    def bl_msg_notification_enabled(self) -> bool: return self.MAIN_CFG["BlockList"].getboolean("blockNewMessageNotification")
    @property
    def bl_order_notification_enabled(self) -> bool: return self.MAIN_CFG["BlockList"].getboolean("blockNewOrderNotification")
    @property
    def bl_cmd_notification_enabled(self) -> bool: return self.MAIN_CFG["BlockList"].getboolean("blockCommandNotification")
    @property
    def include_my_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("includeMyMessages")
    @property
    def include_fp_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("includeFPMessages")
    @property
    def include_bot_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("includeBotMessages")
    @property
    def only_my_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyMyMessages")
    @property
    def only_fp_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyFPMessages")
    @property
    def only_bot_msg_enabled(self) -> bool: return self.MAIN_CFG["NewMessageView"].getboolean("notifyOnlyBotMessages")
    @property
    def block_tg_login(self) -> bool: return self.MAIN_CFG["Telegram"].getboolean("blockLogin")

# END OF FILE FunPayCortex/cortex.py