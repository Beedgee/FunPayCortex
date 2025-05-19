# START OF FILE FunPayCortex/tg_bot/proxy_cp.py

"""
В данном модуле описаны функции для ПУ настроек прокси.
Модуль реализован в виде плагина.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from tg_bot import utils, static_keyboards as skb, keyboards as kb, CBT # keyboards as kb не используется, но оставим на всякий случай
import telebot.apihelper
from Utils.cortex_tools import validate_proxy, cache_proxy_dict, check_proxy
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

if TYPE_CHECKING:
    from cortex import Cortex

from telebot.types import CallbackQuery, Message
import logging
from threading import Thread
from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_proxy_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot
    if not hasattr(tg, 'pr_dict'):
        tg.pr_dict = {}

    def check_one_proxy_thread_target(proxy_str: str):
        try:
            proxy_for_check = {
                "http": f"http://{proxy_str}",
                "https": f"http://{proxy_str}"
            }
            tg.pr_dict[proxy_str] = check_proxy(proxy_for_check)
        except Exception as e:
            logger.warning(f"Ошибка при проверке прокси {proxy_str} в потоке: {e}")
            tg.pr_dict[proxy_str] = False

    def check_all_proxies_periodically():
        if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") and \
           cortex_instance.MAIN_CFG["Proxy"].getboolean("check"):
            logger.info("Запущен периодический чекер прокси.")
            while True:
                proxies_to_check = list(cortex_instance.proxy_dict.values())
                if not proxies_to_check:
                    logger.info("Список прокси для проверки пуст. Пауза перед следующей проверкой.")
                else:
                    logger.info(f"Начинаю проверку {len(proxies_to_check)} прокси...")
                    for proxy_item_str in proxies_to_check:
                        check_one_proxy_thread_target(proxy_item_str)
                        time.sleep(0.1)
                    logger.info("Проверка прокси завершена.")
                
                check_interval_seconds = cortex_instance.MAIN_CFG["Proxy"].getint("checkInterval", 3600)
                time.sleep(check_interval_seconds)
        else:
            logger.info("Периодическая проверка прокси отключена в настройках.")

    if not hasattr(init_proxy_cp, "_checker_thread_started") or not init_proxy_cp._checker_thread_started:
        if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") and cortex_instance.MAIN_CFG["Proxy"].getboolean("check"):
            proxy_checker_thread = Thread(target=check_all_proxies_periodically, daemon=True)
            proxy_checker_thread.start()
            init_proxy_cp._checker_thread_started = True
        else:
            init_proxy_cp._checker_thread_started = False


    def open_proxy_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        proxy_enabled_text = _("proxy_status_enabled") if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") else _("proxy_status_disabled")
        check_enabled_text = _("proxy_check_status_enabled") if cortex_instance.MAIN_CFG["Proxy"].getboolean("check") else _("proxy_check_status_disabled")
        
        current_proxy_display = "<i>(" + _("proxy_not_used_currently") + ")</i>"
        if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable"):
            current_ip = cortex_instance.MAIN_CFG["Proxy"].get("ip")
            current_port = cortex_instance.MAIN_CFG["Proxy"].get("port")
            if current_ip and current_port:
                current_login = cortex_instance.MAIN_CFG["Proxy"].get("login")
                current_pass = cortex_instance.MAIN_CFG["Proxy"].get("password")
                current_proxy_display = f"<code>{f'{current_login}:{current_pass}@' if current_login and current_pass else ''}{current_ip}:{current_port}</code>"
            else:
                 current_proxy_display = "<i>(" + _("proxy_not_selected") + ")</i>"

        check_interval_min = cortex_instance.MAIN_CFG["Proxy"].getint("checkInterval", 3600) // 60

        status_text = f"\n\n🚦 <b>{_('proxy_global_status_header')}:</b>" \
                      f"\n  {_('proxy_module_status_label')} {proxy_enabled_text}" \
                      f"\n  {_('proxy_health_check_label')} {check_enabled_text}" \
                      f"\n  {_('proxy_check_interval_info', check_interval_min)}" \
                      f"\n🔌 <b>{_('proxy_current_in_use_label')}</b> {current_proxy_display}"

        bot.edit_message_text(f'{_("desc_proxy")}{status_text}', c.message.chat.id, c.message.id,
                              reply_markup=kb.proxy(cortex_instance, offset, tg.pr_dict))
        bot.answer_callback_query(c.id)


    def act_add_proxy(c: CallbackQuery):
        offset = int(c.data.split(":")[-1])
        result = bot.send_message(c.message.chat.id, _("act_proxy"), reply_markup=skb.CLEAR_STATE_BTN())
        cortex_instance.telegram.set_state(result.chat.id, result.id, c.from_user.id, CBT.ADD_PROXY, {"offset": offset})
        bot.answer_callback_query(c.id)

    def add_proxy(m: Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        offset = state_data["data"]["offset"] if state_data and state_data.get("data") else 0
        
        reply_kb_on_action = K().add(B(_("gl_back"), callback_data=f"{CBT.PROXY}:{offset}"))
        tg.clear_state(m.chat.id, m.from_user.id, True)
        
        proxy_input_str = m.text.strip()
        try:
            login, password, ip, port = validate_proxy(proxy_input_str)
            canonical_proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
            
            if canonical_proxy_str in cortex_instance.proxy_dict.values():
                bot.send_message(m.chat.id, _("proxy_already_exists", proxy_str=utils.escape(canonical_proxy_str)), reply_markup=reply_kb_on_action)
                return
            
            max_id = max(cortex_instance.proxy_dict.keys(), default=-1) if cortex_instance.proxy_dict else -1
            new_proxy_id = max_id + 1
            
            cortex_instance.proxy_dict[new_proxy_id] = canonical_proxy_str
            cache_proxy_dict(cortex_instance.proxy_dict)
            
            bot.send_message(m.chat.id, _("proxy_added", proxy_str=utils.escape(canonical_proxy_str)), reply_markup=reply_kb_on_action)
            
            if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") and cortex_instance.MAIN_CFG["Proxy"].getboolean("check"):
                new_proxy_thread = Thread(target=check_one_proxy_thread_target, args=(canonical_proxy_str,), daemon=True)
                new_proxy_thread.start()
                
        except ValueError:
            bot.send_message(m.chat.id, _("proxy_format"), reply_markup=reply_kb_on_action)
        except Exception as e:
            logger.error(f"Ошибка при добавлении прокси '{proxy_input_str}': {e}")
            bot.send_message(m.chat.id, _("proxy_adding_error"), reply_markup=reply_kb_on_action)
            logger.debug("TRACEBACK", exc_info=True)

    def choose_proxy(c: CallbackQuery):
        __, offset_str, proxy_id_str = c.data.split(":")
        offset = int(offset_str)
        proxy_id_to_choose = int(proxy_id_str)
        
        chosen_proxy_str = cortex_instance.proxy_dict.get(proxy_id_to_choose)
        
        c.data = f"{CBT.PROXY}:{offset}"
        
        if not chosen_proxy_str:
            bot.answer_callback_query(c.id, _("proxy_select_error_not_found", language=localizer.current_language), show_alert=True)
            open_proxy_list(c)
            return

        try:
            login, password, ip, port = validate_proxy(chosen_proxy_str)
        except ValueError:
            bot.answer_callback_query(c.id, _("proxy_select_error_invalid_format", language=localizer.current_language), show_alert=True)
            open_proxy_list(c)
            return
            
        cortex_instance.MAIN_CFG["Proxy"].update({
            "ip": ip,
            "port": str(port),
            "login": login if login else "",
            "password": password if password else ""
        })
        cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        
        if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable"):
            proxy_for_requests = {
                "http": f"http://{chosen_proxy_str}",
                "https": f"http://{chosen_proxy_str}"
            }
            cortex_instance.account.proxy = proxy_for_requests
            cortex_instance.proxy = proxy_for_requests
            bot.answer_callback_query(c.id, _("proxy_selected_and_applied", proxy_str=utils.escape(chosen_proxy_str), language=localizer.current_language), show_alert=True)
        else:
            bot.answer_callback_query(c.id, _("proxy_selected_not_applied", proxy_str=utils.escape(chosen_proxy_str), language=localizer.current_language), show_alert=True)

        open_proxy_list(c)

    def delete_proxy(c: CallbackQuery):
        __, offset_str, proxy_id_str = c.data.split(":")
        offset = int(offset_str)
        proxy_id_to_delete = int(proxy_id_str)
        
        c.data = f"{CBT.PROXY}:{offset}"
        
        if proxy_id_to_delete in cortex_instance.proxy_dict:
            proxy_to_delete_str = cortex_instance.proxy_dict[proxy_id_to_delete]
            
            current_ip = cortex_instance.MAIN_CFG["Proxy"].get("ip")
            current_port = cortex_instance.MAIN_CFG["Proxy"].get("port")
            current_login = cortex_instance.MAIN_CFG["Proxy"].get("login")
            current_pass = cortex_instance.MAIN_CFG["Proxy"].get("password")
            current_active_proxy_str = f"{f'{current_login}:{current_pass}@' if current_login and current_pass else ''}{current_ip}:{current_port}"

            if cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") and proxy_to_delete_str == current_active_proxy_str:
                bot.answer_callback_query(c.id, _("proxy_undeletable"), show_alert=True)
                open_proxy_list(c)
                return

            del cortex_instance.proxy_dict[proxy_id_to_delete]
            cache_proxy_dict(cortex_instance.proxy_dict)
            
            if proxy_to_delete_str in tg.pr_dict:
                del tg.pr_dict[proxy_to_delete_str]
            
            logger.info(f"Прокси {proxy_to_delete_str} удален пользователем {c.from_user.username}.")
            bot.answer_callback_query(c.id, _("proxy_deleted_successfully", proxy_str=utils.escape(proxy_to_delete_str), language=localizer.current_language), show_alert=True)

            if not cortex_instance.MAIN_CFG["Proxy"].getboolean("enable") and proxy_to_delete_str == current_active_proxy_str:
                for key_to_clear in ("ip", "port", "login", "password"):
                    cortex_instance.MAIN_CFG["Proxy"][key_to_clear] = ""
                cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        else:
            bot.answer_callback_query(c.id, _("proxy_delete_error_not_found", language=localizer.current_language), show_alert=True)

        open_proxy_list(c)

    tg.cbq_handler(open_proxy_list, lambda c: c.data.startswith(f"{CBT.PROXY}:"))
    tg.cbq_handler(act_add_proxy, lambda c: c.data.startswith(f"{CBT.ADD_PROXY}:"))
    tg.cbq_handler(choose_proxy, lambda c: c.data.startswith(f"{CBT.CHOOSE_PROXY}:"))
    tg.cbq_handler(delete_proxy, lambda c: c.data.startswith(f"{CBT.DELETE_PROXY}:"))
    tg.msg_handler(add_proxy, func=lambda m: cortex_instance.telegram.check_state(m.chat.id, m.from_user.id, CBT.ADD_PROXY))


BIND_TO_PRE_INIT = [init_proxy_cp]
# END OF FILE FunPayCortex/tg_bot/proxy_cp.py