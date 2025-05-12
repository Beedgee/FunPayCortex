"""
В данном модуле написан Telegram бот.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from FunPayAPI import Account
from tg_bot.utils import NotificationTypes

if TYPE_CHECKING:
    from cardinal import Cortex # Renamed FPCortex to Cortex

import os
import sys
import time
import random
import string
import psutil
import telebot
from telebot.apihelper import ApiTelegramException
import logging

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery, BotCommand, \
    InputFile
from tg_bot import utils, static_keyboards as skb, keyboards as kb, CBT
from Utils import cardinal_tools, updater # Renamed from Utils to Utils
from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate
telebot.apihelper.ENABLE_MIDDLEWARE = True


class TGBot:
    def __init__(self, cortex_instance: Cortex):
        self.cortex: Cortex = cortex_instance
        self.bot = telebot.TeleBot(self.cortex.MAIN_CFG["Telegram"]["token"], parse_mode="HTML",
                                   allow_sending_without_reply=True, num_threads=5)

        self.file_handlers = {}
        self.attempts = {}
        self.init_messages = []

        self.user_states = {}
        self.notification_settings = utils.load_notification_settings()
        self.answer_templates = utils.load_answer_templates()
        self.authorized_users = utils.load_authorized_users()

        # Ключи команд остаются, описания будут браться из локализации
        self.commands = {
            "menu": "cmd_menu",
            "profile": "cmd_profile",
            "restart": "cmd_restart",
            "check_updates": "cmd_check_updates",
            "update": "cmd_update",
            "golden_key": "cmd_golden_key",
            "ban": "cmd_ban",
            "unban": "cmd_unban",
            "black_list": "cmd_black_list",
            "upload_chat_img": "cmd_upload_chat_img",
            "upload_offer_img": "cmd_upload_offer_img",
            "upload_plugin": "cmd_upload_plugin",
            "test_lot": "cmd_test_lot",
            "logs": "cmd_logs",
            "about": "cmd_about",
            "sys": "cmd_sys",
            "get_backup": "cmd_get_backup",
            "create_backup": "cmd_create_backup",
            "del_logs": "cmd_del_logs",
            "power_off": "cmd_power_off",
            "watermark": "cmd_watermark",
        }
        self.__default_notification_settings = {
            utils.NotificationTypes.ad: 1,
            utils.NotificationTypes.announcement: 1,
            # Добавим критические по умолчанию, если пользователь авторизован
            utils.NotificationTypes.critical: 1 
        }

    # User states (без изменений в логике)
    def get_state(self, chat_id: int, user_id: int) -> dict | None:
        try:
            return self.user_states[chat_id][user_id]
        except KeyError:
            return None

    def set_state(self, chat_id: int, message_id: int, user_id: int, state: str, data: dict | None = None):
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {}
        self.user_states[chat_id][user_id] = {"state": state, "mid": message_id, "data": data or {}}

    def clear_state(self, chat_id: int, user_id: int, del_msg: bool = False) -> int | None:
        try:
            state = self.user_states[chat_id][user_id]
        except KeyError:
            return None

        msg_id = state.get("mid")
        del self.user_states[chat_id][user_id]
        if del_msg:
            try:
                self.bot.delete_message(chat_id, msg_id)
            except:
                pass
        return msg_id

    def check_state(self, chat_id: int, user_id: int, state: str) -> bool:
        try:
            return self.user_states[chat_id][user_id]["state"] == state
        except KeyError:
            return False

    # Notification settings (без изменений в логике)
    def is_notification_enabled(self, chat_id: int | str, notification_type: str) -> bool:
        try:
            return bool(self.notification_settings[str(chat_id)][notification_type])
        except KeyError:
            return False

    def toggle_notification(self, chat_id: int, notification_type: str) -> bool:
        chat_id = str(chat_id)
        if chat_id not in self.notification_settings:
            self.notification_settings[chat_id] = {}

        self.notification_settings[chat_id][notification_type] = not self.is_notification_enabled(chat_id,
                                                                                                  notification_type)
        utils.save_notification_settings(self.notification_settings)
        return self.notification_settings[chat_id][notification_type]

    # handler binders (без изменений в логике)
    def is_file_handler(self, m: Message):
        return self.get_state(m.chat.id, m.from_user.id) and m.content_type in ["photo", "document"]

    def file_handler(self, state, handler):
        self.file_handlers[state] = handler

    def run_file_handlers(self, m: Message):
        if (state := self.get_state(m.chat.id, m.from_user.id)) is None \
                or state["state"] not in self.file_handlers:
            return
        try:
            self.file_handlers[state["state"]](m)
        except:
            logger.error(_("log_tg_handler_error")) # Используем локализацию для логов ошибок
            logger.debug("TRACEBACK", exc_info=True)

    def msg_handler(self, handler, **kwargs):
        bot_instance = self.bot
        @bot_instance.message_handler(**kwargs)
        def run_handler(message: Message):
            try:
                handler(message)
            except:
                logger.error(_("log_tg_handler_error"))
                logger.debug("TRACEBACK", exc_info=True)

    def cbq_handler(self, handler, func, **kwargs):
        bot_instance = self.bot
        @bot_instance.callback_query_handler(func, **kwargs)
        def run_handler(call: CallbackQuery):
            try:
                handler(call)
            except:
                logger.error(_("log_tg_handler_error"))
                logger.debug("TRACEBACK", exc_info=True)

    def mdw_handler(self, handler, **kwargs):
        bot_instance = self.bot
        @bot_instance.middleware_handler(**kwargs)
        def run_handler(bot, update):
            try:
                handler(bot, update)
            except:
                logger.error(_("log_tg_handler_error"))
                logger.debug("TRACEBACK", exc_info=True)

    # Система свой-чужой
    def setup_chat_notifications(self, bot_instance: TGBot, m: Message): # bot_instance (избегаем self как имя параметра)
        chat_id_str = str(m.chat.id)
        user_id = m.from_user.id

        if chat_id_str not in self.notification_settings:
            self.notification_settings[chat_id_str] = self.__default_notification_settings.copy()
            # Если пользователь уже авторизован, включаем ему критические уведомления
            if user_id in self.authorized_users:
                 self.notification_settings[chat_id_str][NotificationTypes.critical] = 1
            else: # Иначе, выключаем, так как __default_notification_settings может их включить
                 self.notification_settings[chat_id_str][NotificationTypes.critical] = 0
            utils.save_notification_settings(self.notification_settings)
        elif user_id in self.authorized_users and not self.is_notification_enabled(chat_id_str, NotificationTypes.critical):
            # Если пользователь авторизовался, а критические уведомления были выключены - включаем
            self.notification_settings[chat_id_str][NotificationTypes.critical] = 1
            utils.save_notification_settings(self.notification_settings)


    def reg_admin(self, m: Message):
        lang = m.from_user.language_code
        if m.chat.type != "private" or (self.attempts.get(m.from_user.id, 0) >= 5) or m.text is None:
            return
        if not self.cortex.block_tg_login and \
                cardinal_tools.check_password(m.text, self.cortex.MAIN_CFG["Telegram"]["secretKeyHash"]):
            # Текст access_granted_notification и access_granted уже локализован
            self.send_notification(text=_("access_granted_notification", m.from_user.username, m.from_user.id),
                                   notification_type=NotificationTypes.critical, pin=True)
            
            # Сохраняем username при авторизации для лучшего отображения в списках
            self.authorized_users[m.from_user.id] = {"username": m.from_user.username or str(m.from_user.id)} 
            utils.save_authorized_users(self.authorized_users)
            
            chat_id_str = str(m.chat.id)
            if chat_id_str not in self.notification_settings:
                self.notification_settings[chat_id_str] = self.__default_notification_settings.copy()
            # Включаем критические уведомления для этого чата после успешной авторизации
            self.notification_settings[chat_id_str][NotificationTypes.critical] = 1
            utils.save_notification_settings(self.notification_settings)
            
            text = _("access_granted", language=lang)
            kb_links = None # Ссылки убраны
            logger.warning(_("log_access_granted", m.from_user.username, m.from_user.id))
        else:
            self.attempts[m.from_user.id] = self.attempts.get(m.from_user.id, 0) + 1
            text = _("access_denied", m.from_user.username, language=lang) # Локализовано
            kb_links = None # Ссылки убраны
            logger.warning(_("log_access_attempt", m.from_user.username, m.from_user.id))
        self.bot.send_message(m.chat.id, text, reply_markup=kb_links)

    def ignore_unauthorized_users(self, c: CallbackQuery):
        logger.warning(_("log_click_attempt", c.from_user.username, c.from_user.id, c.message.chat.username,
                         c.message.chat.id))
        self.attempts[c.from_user.id] = self.attempts.get(c.from_user.id, 0) + 1
        if self.attempts[c.from_user.id] <= 5:
            # adv_fpc уже локализован
            self.bot.answer_callback_query(c.id, _("adv_fpc", language=c.from_user.language_code), show_alert=True)
        return

    # Команды
    def send_settings_menu(self, m: Message):
        self.bot.send_message(m.chat.id, _("desc_main"), reply_markup=skb.SETTINGS_SECTIONS()) # desc_main локализован

    def send_profile(self, m: Message):
        # utils.generate_profile_text должен использовать локализацию внутри себя
        self.bot.send_message(m.chat.id, utils.generate_profile_text(self.cortex),
                              reply_markup=skb.REFRESH_BTN())

    def act_change_cookie(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("act_change_golden_key"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.CHANGE_GOLDEN_KEY)

    def change_cookie(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        golden_key = m.text
        if len(golden_key) != 32 or golden_key != golden_key.lower() or len(golden_key.split()) != 1:
            self.bot.send_message(m.chat.id, _("cookie_incorrect_format")) # Локализовано
            return
        self.bot.delete_message(m.chat.id, m.id) # Удаляем сообщение с ключом для безопасности
        new_account = Account(golden_key, self.cortex.account.user_agent, proxy=self.cortex.proxy,
                              locale=self.cortex.account.locale)
        try:
            new_account.get()
        except:
            logger.warning(_("cookie_error")) # Локализовано (лог тоже)
            logger.debug("TRACEBACK", exc_info=True)
            self.bot.send_message(m.chat.id, _("cookie_error")) # Локализовано
            return

        one_acc = False
        if new_account.id == self.cortex.account.id or self.cortex.account.id is None:
            one_acc = True
            self.cortex.account.golden_key = golden_key
            try:
                self.cortex.account.get()
            except:
                logger.warning(_("cookie_error"))
                logger.debug("TRACEBACK", exc_info=True)
                self.bot.send_message(m.chat.id, _("cookie_error"))
                return
            accs = f" (<a href='https://funpay.com/users/{new_account.id}/'>{new_account.username}</a>)"
        else:
            accs = f" (<a href='https://funpay.com/users/{self.cortex.account.id}/'>" \
                   f"{self.cortex.account.username}</a> ➔ <a href='https://funpay.com/users/{new_account.id}/'>" \
                   f"{new_account.username}</a>)"

        self.cortex.MAIN_CFG.set("FunPay", "golden_key", golden_key)
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        # cookie_changed и cookie_changed2 локализованы
        self.bot.send_message(m.chat.id, f'{_("cookie_changed", accs)}{_("cookie_changed2") if not one_acc else ""}',
                              disable_web_page_preview=True)

    def update_profile(self, c: CallbackQuery):
        new_msg = self.bot.send_message(c.message.chat.id, _("updating_profile")) # Локализовано
        try:
            self.cortex.account.get()
            self.cortex.balance = self.cortex.get_balance()
        except:
            self.bot.edit_message_text(_("profile_updating_error"), new_msg.chat.id, new_msg.id) # Локализовано
            logger.debug("TRACEBACK", exc_info=True)
            self.bot.answer_callback_query(c.id)
            return

        self.bot.delete_message(new_msg.chat.id, new_msg.id)
        self.bot.edit_message_text(utils.generate_profile_text(self.cortex), c.message.chat.id,
                                   c.message.id, reply_markup=skb.REFRESH_BTN())

    def act_manual_delivery_test(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("create_test_ad_key"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.MANUAL_AD_TEST)

    def manual_delivery_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        lot_name = m.text.strip()
        key = "".join(random.sample(string.ascii_letters + string.digits, 50))
        self.cortex.delivery_tests[key] = lot_name

        logger.info(_("log_new_ad_key", m.from_user.username, m.from_user.id, lot_name, key))
        self.bot.send_message(m.chat.id, _("test_ad_key_created", utils.escape(lot_name), key)) # Локализовано

    def act_ban(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("act_blacklist"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.BAN)

    def ban(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        nickname = m.text.strip()

        if nickname in self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("already_blacklisted", utils.escape(nickname))) # Локализовано, добавил escape
            return

        self.cortex.blacklist.append(nickname)
        cardinal_tools.cache_blacklist(self.cortex.blacklist)
        logger.info(_("log_user_blacklisted", m.from_user.username, m.from_user.id, nickname))
        self.bot.send_message(m.chat.id, _("user_blacklisted", utils.escape(nickname))) # Локализовано, добавил escape

    def act_unban(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("act_unban"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.UNBAN)

    def unban(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        nickname = m.text.strip()
        if nickname not in self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("not_blacklisted", utils.escape(nickname))) # Локализовано, добавил escape
            return
        self.cortex.blacklist.remove(nickname)
        cardinal_tools.cache_blacklist(self.cortex.blacklist)
        logger.info(_("log_user_unbanned", m.from_user.username, m.from_user.id, nickname))
        self.bot.send_message(m.chat.id, _("user_unbanned", utils.escape(nickname))) # Локализовано, добавил escape

    def send_ban_list(self, m: Message):
        if not self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("blacklist_empty")) # Локализовано
            return
        blacklist_str = "\n".join(f"🚫 <code>{utils.escape(i)}</code>" for i in sorted(self.cortex.blacklist, key=lambda x: x.lower())) # Добавил эмодзи и escape
        self.bot.send_message(m.chat.id, f"<b>Черный список:</b>\n{blacklist_str}" if blacklist_str else _("blacklist_empty"))

    def act_edit_watermark(self, m: Message):
        watermark = self.cortex.MAIN_CFG["Other"]["watermark"]
        watermark_display = f"\n\nТекущий: <code>{utils.escape(watermark)}</code>" if watermark else ""
        result = self.bot.send_message(m.chat.id, _("act_edit_watermark").format(watermark_display), # Локализовано
                                       reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.EDIT_WATERMARK)

    def edit_watermark(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        watermark_text = m.text if m.text != "-" else ""
        if re.fullmatch(r"\[[a-zA-Z]+]", watermark_text): # Проверка на недопустимые символы
            self.bot.reply_to(m, _("watermark_error")) # Локализовано
            return
        
        # Логика для preview (можно оставить или убрать, если не используется)
        preview_html = f"<a href=\"https://sfunpay.com/s/chat/zb/wl/zbwl4vwc8cc1wsftqnx5.jpg\">⁢</a>" # Стандартный preview
        if any(i.lower() in watermark_text.lower() for i in ("🧠", "fpcx", "cortex", "кортекс")):
            preview_html = f"<a href=\"https://sfunpay.com/s/chat/kd/8i/kd8isyquw660kcueck3g.jpg\">⁢</a>" # FPCortex preview

        self.cortex.MAIN_CFG["Other"]["watermark"] = watermark_text
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        if watermark_text:
            logger.info(_("log_watermark_changed", m.from_user.username, m.from_user.id, watermark_text))
            self.bot.reply_to(m, preview_html + _("watermark_changed", utils.escape(watermark_text))) # Локализовано
        else:
            logger.info(_("log_watermark_deleted", m.from_user.username, m.from_user.id))
            self.bot.reply_to(m, preview_html + _("watermark_deleted")) # Локализовано

    def send_logs(self, m: Message):
        if not os.path.exists("logs/log.log"):
            self.bot.send_message(m.chat.id, _("logfile_not_found")) # Локализовано
        else:
            self.bot.send_message(m.chat.id, _("logfile_sending")) # Локализовано
            try:
                with open("logs/log.log", "r", encoding="utf-8") as f:
                    # Сообщение о режиме получения сообщений
                    mode_info = _("gs_old_msg_mode").replace("{} ", "") if self.cortex.old_mode_enabled else _("old_mode_help").split('\n')[0].replace("<b>","").replace("</b>","").replace("🚀","").strip()
                    
                    self.bot.send_document(m.chat.id, f,
                                           caption=f"📄 Лог-файл FPCortex\nРежим сообщений: <i>{mode_info}</i>")
                    f.seek(0)
                    file_content = f.read()
                    # Упрощенный вывод последней ошибки
                    last_traceback_start = file_content.rfind("TRACEBACK")
                    if last_traceback_start != -1:
                        # Берем контекст до и после TRACEBACK
                        context_before = file_content[max(0, last_traceback_start - 200):last_traceback_start]
                        error_text_block = file_content[last_traceback_start:]
                        # Обрезаем блок ошибки, если он слишком длинный
                        error_text_block = error_text_block[:1000] + "..." if len(error_text_block) > 1000 else error_text_block
                        
                        result = f"<b>Последняя ошибка в логах:</b>\n\n...<code>{utils.escape(context_before.splitlines()[-1] if context_before.splitlines() else '')}\n{utils.escape(error_text_block)}</code>"
                        
                        # Разбиваем на сообщения, если слишком длинно
                        for chunk in telebot.util.smart_split(result, 4096):
                            self.bot.send_message(m.chat.id, chunk)
                            time.sleep(0.3) # Небольшая задержка между сообщениями
                    else:
                        self.bot.send_message(m.chat.id, "👍 Ошибок в последнем лог-файле не найдено.")
            except Exception as e:
                logger.error(f"Ошибка при отправке логов: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                self.bot.send_message(m.chat.id, _("logfile_error")) # Локализовано

    def del_logs(self, m: Message):
        logger.info(
            f"[IMPORTANT] Удаляю старые логи по запросу пользователя $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET.")
        deleted_count = 0
        for file_name in os.listdir("logs"):
            if not file_name.endswith(".log"): # Удаляем все, КРОМЕ текущего log.log
                try:
                    os.remove(os.path.join("logs", file_name))
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Не удалось удалить файл {file_name}: {e}")
                    continue
        self.bot.send_message(m.chat.id, _("logfile_deleted", deleted_count)) # Локализовано

    def about(self, m: Message):
        self.bot.send_message(m.chat.id, _("about", self.cortex.VERSION)) # Локализовано

    def check_updates(self, m: Message):
        curr_tag = f"v{self.cortex.VERSION}"
        releases = updater.get_new_releases(curr_tag)
        if isinstance(releases, int):
            # Все сообщения об ошибках обновления уже локализованы
            errors = {
                1: ["update_no_tags", ()],
                2: ["update_lasted", (curr_tag,)],
                3: ["update_get_error", ()],
            }
            self.bot.send_message(m.chat.id, _(errors[releases][0], *errors[releases][1]))
            return
        # Эта часть кода не будет достигнута, так как обновления отключены
        # for release in releases:
        #     self.bot.send_message(m.chat.id, _("update_available", release.name, release.description))
        #     time.sleep(1)
        # self.bot.send_message(m.chat.id, _("update_update"))

    def get_backup(self, m: Message):
        logger.info(
            f"[IMPORTANT] Запрос резервной копии от $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET.")
        backup_path = "backup.zip"
        if os.path.exists(backup_path):
            with open(backup_path, 'rb') as file:
                modification_timestamp = os.path.getmtime(backup_path)
                formatted_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(modification_timestamp))
                # update_backup уже локализован
                self.bot.send_document(chat_id=m.chat.id, document=InputFile(file),
                                       caption=f'{_("update_backup")}\n\n🗓️ Дата создания: {formatted_time}')
        else:
            self.bot.send_message(m.chat.id, _("update_backup_not_found")) # Локализовано

    def create_backup(self, m: Message):
        if updater.create_backup(): # create_backup возвращает True при ошибке, False при успехе
            self.bot.send_message(m.chat.id, _("update_backup_error")) # Локализовано
            return False
        # Сообщение об успехе уже включено в get_backup
        self.get_backup(m)
        return True

    def update(self, m: Message):
        curr_tag = f"v{self.cortex.VERSION}"
        releases = updater.get_new_releases(curr_tag) # Вернет 2 (последняя версия)
        if isinstance(releases, int):
            errors = {
                1: ["update_no_tags", ()],
                2: ["update_lasted", (curr_tag,)],
                3: ["update_get_error", ()],
            }
            self.bot.send_message(m.chat.id, _(errors[releases][0], *errors[releases][1]))
            return
        # Код ниже не будет выполнен из-за отключенных обновлений
        # if not self.create_backup(m):
        #     return
        # release = releases[-1]
        # if updater.download_zip(release.sources_link) \
        #         or (release_folder := updater.extract_update_archive()) == 1:
        #     self.bot.send_message(m.chat.id, _("update_download_error"))
        #     return
        # self.bot.send_message(m.chat.id, _("update_downloaded", release.name, str(len(releases) - 1)))
        #
        # if updater.install_release(release_folder):
        #     self.bot.send_message(m.chat.id, _("update_install_error"))
        #     return
        #
        # if getattr(sys, 'frozen', False):
        #     self.bot.send_message(m.chat.id, _("update_done_exe"))
        # else:
        #     self.bot.send_message(m.chat.id, _("update_done"))

    def send_system_info(self, m: Message):
        current_timestamp = int(time.time())
        uptime_seconds = current_timestamp - self.cortex.start_time

        ram_info = psutil.virtual_memory()
        cpu_usage_per_core = "\n".join(
            f"    Core {i+1}:  <code>{usage}%</code>" for i, usage in enumerate(psutil.cpu_percent(percpu=True))) # Нумерация с 1
        # sys_info уже локализован
        self.bot.send_message(m.chat.id, _("sys_info", cpu_usage_per_core, psutil.Process().cpu_percent(),
                                           ram_info.total // 1048576, ram_info.used // 1048576, ram_info.free // 1048576,
                                           psutil.Process().memory_info().rss // 1048576,
                                           cardinal_tools.time_to_str(uptime_seconds), m.chat.id))

    def restart_cardinal(self, m: Message):
        self.bot.send_message(m.chat.id, _("restarting")) # Локализовано
        cardinal_tools.restart_program()

    def ask_power_off(self, m: Message):
        self.bot.send_message(m.chat.id, _("power_off_0"), reply_markup=kb.power_off(self.cortex.instance_id, 0)) # Локализовано

    def cancel_power_off(self, c: CallbackQuery):
        self.bot.edit_message_text(_("power_off_cancelled"), c.message.chat.id, c.message.id) # Локализовано
        self.bot.answer_callback_query(c.id)

    def power_off(self, c: CallbackQuery):
        split_data = c.data.split(":")
        current_stage = int(split_data[1])
        instance_id_from_cb = int(split_data[2])

        if instance_id_from_cb != self.cortex.instance_id:
            self.bot.edit_message_text(_("power_off_error"), c.message.chat.id, c.message.id) # Локализовано
            self.bot.answer_callback_query(c.id)
            return

        if current_stage == 6: # Последний этап подтверждения
            self.bot.edit_message_text(_("power_off_6"), c.message.chat.id, c.message.id) # Локализовано
            self.bot.answer_callback_query(c.id)
            cardinal_tools.shut_down()
            return

        # Отображаем следующее сообщение из цепочки power_off_X
        self.bot.edit_message_text(_(f"power_off_{current_stage}"), c.message.chat.id, c.message.id,
                                   reply_markup=kb.power_off(instance_id_from_cb, current_stage))
        self.bot.answer_callback_query(c.id)

    # Чат FunPay
    def act_send_funpay_message(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id = int(split_data[1])
        username = split_data[2] if len(split_data) > 2 else None
        
        result_msg = self.bot.send_message(c.message.chat.id, _("enter_msg_text"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id,
                       CBT.SEND_FP_MESSAGE, {"node_id": node_id, "username": username})
        self.bot.answer_callback_query(c.id)

    def send_funpay_message(self, message: Message):
        state_data = self.get_state(message.chat.id, message.from_user.id)["data"]
        node_id, username = state_data["node_id"], state_data["username"]
        self.clear_state(message.chat.id, message.from_user.id, True)
        response_text_to_send = message.text.strip()
        
        send_success = self.cortex.send_message(node_id, response_text_to_send, username, watermark=False)
        
        reply_kb = kb.reply(node_id, username, again=True, extend=True) # Клавиатура уже обновлена
        if send_success:
            self.bot.reply_to(message, _("msg_sent", node_id, username or "Пользователь"), reply_markup=reply_kb) # Локализовано
        else:
            self.bot.reply_to(message, _("msg_sending_error", node_id, username or "Пользователь"), reply_markup=reply_kb) # Локализовано

    def act_upload_image(self, m: Message):
        # Определяем, для чата или для лота загружается изображение
        cbt_state = CBT.UPLOAD_CHAT_IMAGE if m.text.startswith("/upload_chat_img") else CBT.UPLOAD_OFFER_IMAGE
        result_msg = self.bot.send_message(m.chat.id, _("send_img"), reply_markup=skb.CLEAR_STATE_BTN()) # Локализовано
        self.set_state(m.chat.id, result_msg.id, m.from_user.id, cbt_state)

    def act_edit_greetings_text(self, c: CallbackQuery):
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_message_text", "v_chat_id", "v_chat_name", "v_photo", "v_sleep"]
        # v_edit_greeting_text и v_list уже локализованы
        text_to_send = f"{_('v_edit_greeting_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_GREETINGS_TEXT)
        self.bot.answer_callback_query(c.id)

    def edit_greetings_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_greeting_text = m.text.strip()
        self.cortex.MAIN_CFG["Greetings"]["greetingsText"] = new_greeting_text
        logger.info(_("log_greeting_changed", m.from_user.username, m.from_user.id, new_greeting_text))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        # Кнопки gl_back и gl_edit уже локализованы
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:gr"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_GREETINGS_TEXT))
        self.bot.reply_to(m, _("greeting_changed"), reply_markup=reply_keyboard) # Локализовано

    def act_edit_greetings_cooldown(self, c: CallbackQuery):
        # v_edit_greeting_cooldown уже локализован
        text_to_send = _('v_edit_greeting_cooldown')
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_GREETINGS_COOLDOWN)
        self.bot.answer_callback_query(c.id)

    def edit_greetings_cooldown(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        try:
            cooldown_days = float(m.text.replace(",", ".")) # Замена запятой на точку для float
            if cooldown_days < 0: raise ValueError("Cooldown не может быть отрицательным")
        except ValueError:
            self.bot.reply_to(m, _("gl_error_try_again") + " (введите число, например, 0.5 или 1)") # Локализовано, добавлено пояснение
            return
            
        self.cortex.MAIN_CFG["Greetings"]["greetingsCooldown"] = str(cooldown_days)
        logger.info(_("log_greeting_cooldown_changed", m.from_user.username, m.from_user.id, str(cooldown_days)))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:gr"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_GREETINGS_COOLDOWN))
        self.bot.reply_to(m, _("greeting_cooldown_changed", str(cooldown_days)), reply_markup=reply_keyboard) # Локализовано

    def act_edit_order_confirm_reply_text(self, c: CallbackQuery):
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_order_id", "v_order_link", "v_order_title", "v_game", "v_category", "v_category_fullname",
                     "v_photo", "v_sleep"]
        text_to_send = f"{_('v_edit_order_confirm_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT)
        self.bot.answer_callback_query(c.id)

    def edit_order_confirm_reply_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_reply_text = m.text.strip()
        self.cortex.MAIN_CFG["OrderConfirm"]["replyText"] = new_reply_text
        logger.info(_("log_order_confirm_changed", m.from_user.username, m.from_user.id, new_reply_text))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:oc"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT))
        self.bot.reply_to(m, _("order_confirm_changed"), reply_markup=reply_keyboard) # Локализовано

    def act_edit_review_reply_text(self, c: CallbackQuery):
        stars_count = int(c.data.split(":")[1])
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_order_id", "v_order_link", "v_order_title", "v_order_params",
                     "v_order_desc_and_params", "v_order_desc_or_params", "v_game", "v_category", "v_category_fullname"]
        # v_edit_review_reply_text уже локализован
        text_to_send = f"{_('v_edit_review_reply_text', '⭐' * stars_count)}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_REVIEW_REPLY_TEXT, {"stars": stars_count})
        self.bot.answer_callback_query(c.id)

    def edit_review_reply_text(self, m: Message):
        stars_count = self.get_state(m.chat.id, m.from_user.id)["data"]["stars"]
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_review_reply = m.text.strip()
        self.cortex.MAIN_CFG["ReviewReply"][f"star{stars_count}ReplyText"] = new_review_reply
        logger.info(_("log_review_reply_changed", m.from_user.username, m.from_user.id, stars_count, new_review_reply))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:rr"),
                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{stars_count}"))
        self.bot.reply_to(m, _("review_reply_changed", '⭐' * stars_count), reply_markup=reply_keyboard) # Локализовано

    def open_reply_menu(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id, username = int(split_data[1]), split_data[2]
        is_again_reply = int(split_data[3])
        should_extend = True if len(split_data) > 4 and int(split_data[4]) else False
        
        self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=kb.reply(node_id, username, bool(is_again_reply), should_extend))

    def extend_new_message_notification(self, c: CallbackQuery):
        chat_id_str, username = c.data.split(":")[1:]
        try:
            chat_obj = self.cortex.account.get_chat(int(chat_id_str))
        except Exception as e:
            logger.warning(f"Не удалось получить чат {chat_id_str} для расширения: {e}")
            self.bot.answer_callback_query(c.id, _("get_chat_error"), show_alert=True) # Локализовано
            return

        text_to_send = ""
        if chat_obj.looking_link: # Если пользователь что-то смотрит на FunPay
            text_to_send += f"<b>{_('viewing')}:</b> <a href=\"{chat_obj.looking_link}\">{utils.escape(chat_obj.looking_text)}</a>\n\n"

        # Последние 10 сообщений
        chat_messages = chat_obj.messages[-10:]
        last_author_id = -1
        last_by_bot_flag = False
        last_author_badge = None
        last_by_fpcortex = False # Используем новое имя

        for msg_item in chat_messages:
            author_prefix = ""
            # Определение автора сообщения
            if msg_item.author_id == last_author_id and \
               msg_item.by_bot == last_by_bot_flag and \
               msg_item.badge == last_author_badge and \
               last_by_fpcortex == msg_item.by_bot: # Проверяем, был ли предыдущий от FPCortex
                pass # Не добавляем префикс, если автор тот же и тип тот же
            elif msg_item.author_id == self.cortex.account.id:
                author_prefix = f"<i><b>🤖 {_('you')} (<i>FPCortex</i>):</b></i> " if msg_item.by_bot else f"<i><b>🫵 {_('you')}:</b></i> "
                if msg_item.is_autoreply: # Если это автоответ от FPCortex (например, автовыдача)
                    author_prefix = f"<i><b>📦 {_('you')} ({utils.escape(msg_item.badge)}):</b></i> "
            elif msg_item.author_id == 0: # Системное сообщение FunPay
                author_prefix = f"<i><b>🔵 {utils.escape(msg_item.author)}: </b></i>"
            elif msg_item.is_employee: # Сотрудник поддержки FunPay
                author_prefix = f"<i><b>🆘 {utils.escape(msg_item.author)} ({utils.escape(msg_item.badge)}): </b></i>"
            elif msg_item.author == msg_item.chat_name: # Обычный пользователь
                author_prefix = f"<i><b>👤 {utils.escape(msg_item.author)}: </b></i>"
                if msg_item.is_autoreply: # Если это автоответ от другого бота
                    author_prefix = f"<i><b>🛍️ {utils.escape(msg_item.author)} ({utils.escape(msg_item.badge)}):</b></i> "
                elif msg_item.author in self.cortex.blacklist: # Пользователь в ЧС
                    author_prefix = f"<i><b>🚷 {utils.escape(msg_item.author)}: </b></i>"
                elif msg_item.by_bot and msg_item.author_id != self.cortex.account.id : # Сообщение от другого бота (не FPCortex)
                     author_prefix = f"<i><b>👾 {utils.escape(msg_item.author)}: </b></i>" # Другой эмодзи для сторонних ботов
            else: # Другой тип сообщения от FunPay (например, арбитр)
                author_prefix = f"<i><b>⚖️ {utils.escape(msg_item.author)} ({_('support')}): </b></i>"
            
            # Форматирование текста сообщения или ссылки на изображение
            message_content = f"<code>{utils.escape(msg_item.text)}</code>" if msg_item.text else \
                f"<a href=\"{msg_item.image_link}\">" \
                f"{utils.escape(msg_item.image_name) if self.cortex.MAIN_CFG['NewMessageView'].getboolean('showImageName') and not (msg_item.author_id == self.cortex.account.id and msg_item.by_bot) else _('photo')}</a>"
            
            text_to_send += f"{author_prefix}{message_content}\n\n"
            
            # Сохраняем данные о последнем авторе для группировки сообщений
            last_author_id = msg_item.author_id
            last_by_bot_flag = msg_item.by_bot
            last_author_badge = msg_item.badge
            last_by_fpcortex = msg_item.by_bot and msg_item.author_id == self.cortex.account.id # Флаг, что это сообщение от FPCortex

        # Убираем лишние переносы строк в конце
        text_to_send = text_to_send.strip()
        if not text_to_send: text_to_send = "<i>(Нет сообщений для отображения)</i>"

        self.bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id,
                                   reply_markup=kb.reply(int(chat_id_str), username, False, False))
        self.bot.answer_callback_query(c.id)


    # Ордер
    def ask_confirm_refund(self, call: CallbackQuery):
        split_data = call.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        
        # Клавиатура уже обновлена в keyboards.py
        refund_confirm_keyboard = kb.new_order(order_id, username, node_id, confirmation=True)
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=refund_confirm_keyboard)
        self.bot.answer_callback_query(call.id)

    def cancel_refund(self, call: CallbackQuery):
        split_data = call.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        
        # Клавиатура уже обновлена
        order_keyboard = kb.new_order(order_id, username, node_id)
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=order_keyboard)
        self.bot.answer_callback_query(call.id)

    def refund(self, c: CallbackQuery):
        split_data = c.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        
        progress_message = None
        attempts_left = 3
        refund_successful = False

        while attempts_left > 0:
            try:
                self.cortex.account.refund(order_id)
                refund_successful = True
                break # Успех, выходим из цикла
            except Exception as e:
                logger.error(f"Ошибка возврата заказа #{order_id}, попытка {4 - attempts_left}: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                # refund_attempt уже локализован
                attempt_message_text = _("refund_attempt", order_id, attempts_left -1) # -1 потому что одна попытка уже была
                if not progress_message:
                    progress_message = self.bot.send_message(c.message.chat.id, attempt_message_text)
                else:
                    self.bot.edit_message_text(attempt_message_text, progress_message.chat.id, progress_message.id)
                attempts_left -= 1
                if attempts_left > 0: time.sleep(1) # Пауза перед следующей попыткой

        final_message_text = ""
        if refund_successful:
            final_message_text = _("refund_complete", order_id) # Локализовано
        else:
            final_message_text = _("refund_error", order_id) # Локализовано

        if not progress_message: # Если возврат удался с первой попытки
            self.bot.send_message(c.message.chat.id, final_message_text)
        else:
            self.bot.edit_message_text(final_message_text, progress_message.chat.id, progress_message.id)

        # Обновляем клавиатуру заказа (кнопка возврата будет убрана, если успешно)
        order_keyboard_after_refund = kb.new_order(order_id, username, node_id, no_refund=refund_successful)
        self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=order_keyboard_after_refund)
        self.bot.answer_callback_query(c.id)

    def open_order_menu(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id, username, order_id = int(split_data[1]), split_data[2], split_data[3]
        no_refund_flag = bool(int(split_data[4]))
        
        self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=kb.new_order(order_id, username, node_id, no_refund=no_refund_flag))

    # Панель управления
    def open_cp(self, c: CallbackQuery):
        self.bot.edit_message_text(_("desc_main"), c.message.chat.id, c.message.id, # Локализовано
                                   reply_markup=skb.SETTINGS_SECTIONS())
        self.bot.answer_callback_query(c.id)

    def open_cp2(self, c: CallbackQuery):
        self.bot.edit_message_text(_("desc_main"), c.message.chat.id, c.message.id, # Локализовано
                                   reply_markup=skb.SETTINGS_SECTIONS_2())
        self.bot.answer_callback_query(c.id)

    def switch_param(self, c: CallbackQuery):
        split_data = c.data.split(":")
        section_name, option_name = split_data[1], split_data[2]
        
        if section_name == "FunPay" and option_name == "oldMsgGetMode":
            self.cortex.switch_msg_get_mode()
        else:
            current_value_str = self.cortex.MAIN_CFG[section_name].get(option_name, "0") # Безопасное получение
            new_value = str(int(not int(current_value_str)))
            self.cortex.MAIN_CFG[section_name][option_name] = new_value
            self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")

        # Словарь для обновления клавиатур соответствующих секций
        section_keyboards_map = {
            "FunPay": kb.main_settings,
            "BlockList": kb.blacklist_settings,
            "NewMessageView": kb.new_message_view_settings,
            "Greetings": kb.greeting_settings,
            "OrderConfirm": kb.order_confirm_reply_settings,
            "ReviewReply": kb.review_reply_settings,
            "Proxy": lambda ctx, offset: kb.proxy(ctx, offset, self.cortex.telegram.pr_dict if hasattr(self.cortex.telegram, 'pr_dict') else {}) # Для прокси нужен offset
        }
        
        # Обновляем клавиатуру
        if section_name == "Telegram": # Для авторизованных пользователей отдельная логика
             offset_val = int(split_data[3]) if len(split_data) > 3 else 0
             self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                               reply_markup=kb.authorized_users(self.cortex, offset=offset_val))
        elif section_name == "Proxy":
             offset_val = int(split_data[3]) if len(split_data) > 3 else 0
             # pr_dict должен быть доступен в TGBot, если он используется в keyboards.proxy
             pr_dict_for_kb = self.cortex.telegram.pr_dict if hasattr(self.cortex.telegram, 'pr_dict') else {}
             self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                                reply_markup=kb.proxy(self.cortex, offset_val, pr_dict_for_kb))
        elif section_name in section_keyboards_map:
            self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                               reply_markup=section_keyboards_map[section_name](self.cortex))
        else: # Если для секции нет специальной клавиатуры, просто отвечаем на колбэк
            self.bot.answer_callback_query(c.id, "✅ Настройка изменена!")


        logger.info(_("log_param_changed", c.from_user.username, c.from_user.id, option_name, section_name,
                      self.cortex.MAIN_CFG[section_name][option_name]))
        self.bot.answer_callback_query(c.id) # Ответ на колбэк, если он еще не был дан

    def switch_chat_notification(self, c: CallbackQuery):
        split_data = c.data.split(":")
        chat_id_for_notif, notification_type_str = int(split_data[1]), split_data[2]

        toggle_result = self.toggle_notification(chat_id_for_notif, notification_type_str)
        logger.info(_("log_notification_switched", c.from_user.username, c.from_user.id,
                      notification_type_str, c.message.chat.id, toggle_result))
        
        # Определяем, какую клавиатуру настроек обновлять
        reply_kb_generator = kb.notifications_settings # По умолчанию - общие настройки уведомлений
        if notification_type_str in [NotificationTypes.announcement, NotificationTypes.ad]:
            reply_kb_generator = kb.announcements_settings
        
        self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=reply_kb_generator(self.cortex, c.message.chat.id))
        self.bot.answer_callback_query(c.id)

    def open_settings_section(self, c: CallbackQuery):
        section_key = c.data.split(":")[1]
        # Все desc_* и названия клавиатур уже локализованы
        sections_map = {
            "lang": (_("desc_lang"), kb.language_settings, [self.cortex]),
            "main": (_("desc_gs"), kb.main_settings, [self.cortex]),
            "tg": (_("desc_ns", c.message.chat.id), kb.notifications_settings, [self.cortex, c.message.chat.id]),
            "bl": (_("desc_bl"), kb.blacklist_settings, [self.cortex]),
            "ar": (_("desc_ar"), skb.AR_SETTINGS, []),
            "ad": (_("desc_ad"), skb.AD_SETTINGS, []),
            "mv": (_("desc_mv"), kb.new_message_view_settings, [self.cortex]),
            "rr": (_("desc_or"), kb.review_reply_settings, [self.cortex]),
            "gr": (_("desc_gr", utils.escape(self.cortex.MAIN_CFG['Greetings']['greetingsText'])),
                   kb.greeting_settings, [self.cortex]),
            "oc": (_("desc_oc", utils.escape(self.cortex.MAIN_CFG['OrderConfirm']['replyText'])),
                   kb.order_confirm_reply_settings, [self.cortex])
        }

        current_section_data = sections_map.get(section_key)
        if current_section_data:
            desc_text, kb_generator, kb_args = current_section_data
            self.bot.edit_message_text(desc_text, c.message.chat.id, c.message.id, reply_markup=kb_generator(*kb_args))
        else:
            # Обработка неизвестной секции, если нужно
            self.bot.answer_callback_query(c.id, "⚠️ Секция не найдена!", show_alert=True)
            return
        self.bot.answer_callback_query(c.id)

    # Прочее
    def cancel_action(self, call: CallbackQuery):
        # Кнопка "Отмена" уже локализована через _("gl_cancel") в skb.CLEAR_STATE_BTN
        clear_result = self.clear_state(call.message.chat.id, call.from_user.id, True)
        if clear_result is None: # Если состояния не было, просто отвечаем
            self.bot.answer_callback_query(call.id)
        # Сообщение об отмене не требуется, так как сообщение с запросом ввода удаляется

    def param_disabled(self, c: CallbackQuery):
        # param_disabled уже локализован
        self.bot.answer_callback_query(c.id, _("param_disabled"), show_alert=True)

    def send_announcements_kb(self, m: Message):
        # desc_an и клавиатура announcements_settings уже локализованы
        self.bot.send_message(m.chat.id, _("desc_an"), reply_markup=kb.announcements_settings(self.cortex, m.chat.id))

    def send_review_reply_text(self, c: CallbackQuery):
        stars_count = int(c.data.split(":")[1])
        reply_text = self.cortex.MAIN_CFG["ReviewReply"][f"star{stars_count}ReplyText"]
        
        # Кнопки gl_back и gl_edit уже локализованы
        edit_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:rr"),
                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{stars_count}"))
        
        if not reply_text:
            # review_reply_empty уже локализован
            self.bot.send_message(c.message.chat.id, _("review_reply_empty", "⭐" * stars_count), reply_markup=edit_keyboard)
        else:
            # review_reply_text уже локализован
            self.bot.send_message(c.message.chat.id, _("review_reply_text", "⭐" * stars_count,
                                                       utils.escape(reply_text)), # Экранируем текст ответа
                                  reply_markup=edit_keyboard)
        self.bot.answer_callback_query(c.id)

    def send_old_mode_help_text(self, c: CallbackQuery):
        self.bot.answer_callback_query(c.id)
        self.bot.send_message(c.message.chat.id, _("old_mode_help")) # Локализовано

    def empty_callback(self, c: CallbackQuery):
        # Можно изменить или убрать это сообщение, если оно не нужно
        self.bot.answer_callback_query(c.id, "👍") 

    def switch_lang(self, c: CallbackQuery):
        selected_lang = c.data.split(":")[1]
        Localizer(selected_lang) # Переключаем язык локализатора
        self.cortex.MAIN_CFG["Other"]["language"] = selected_lang
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        
        # Обновляем меню команд на новом языке
        self.setup_commands() 
        
        alert_message = None
        if selected_lang == "en":
            alert_message = "The translation may be incomplete and contain errors.\n\n" \
                            "If you find errors, please let @beedge know.\n\nThank you :)"
        elif selected_lang == "uk":
            alert_message = "Переклад може бути неповним та містити помилки.\n" \
                            "Повідомте @beedge, якщо знайдете неточності."
        # elif selected_lang == "ru": # Сообщение для русского можно убрать или оставить
        #     alert_message = '«А я сейчас вам покажу, откуда на Беларусь готовилось нападение»'
            
        if alert_message:
            self.bot.answer_callback_query(c.id, alert_message, show_alert=True)
        else:
            self.bot.answer_callback_query(c.id) # Простой ответ, если нет специального сообщения
            
        # Обновляем текущее меню на новом языке
        c.data = f"{CBT.CATEGORY}:lang"
        self.open_settings_section(c)

    def __register_handlers(self):
        self.mdw_handler(self.setup_chat_notifications, update_types=['message'])
        self.msg_handler(self.reg_admin, func=lambda msg: msg.from_user.id not in self.authorized_users,
                         content_types=['text', 'document', 'photo', 'sticker'])
        self.cbq_handler(self.ignore_unauthorized_users, lambda c: c.from_user.id not in self.authorized_users)
        self.cbq_handler(self.param_disabled, lambda c: c.data.startswith(CBT.PARAM_DISABLED))
        self.msg_handler(self.run_file_handlers, content_types=["photo", "document"],
                         func=lambda m: self.is_file_handler(m))

        # Команды (логика без изменений)
        self.msg_handler(self.send_settings_menu, commands=["menu", "start"])
        self.msg_handler(self.send_profile, commands=["profile"])
        self.msg_handler(self.act_change_cookie, commands=["change_cookie", "golden_key"])
        self.msg_handler(self.change_cookie, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.CHANGE_GOLDEN_KEY))
        self.cbq_handler(self.update_profile, lambda c: c.data == CBT.UPDATE_PROFILE)
        self.msg_handler(self.act_manual_delivery_test, commands=["test_lot"])
        self.msg_handler(self.act_upload_image, commands=["upload_chat_img", "upload_offer_img"])
        self.cbq_handler(self.act_edit_greetings_text, lambda c: c.data == CBT.EDIT_GREETINGS_TEXT)
        self.msg_handler(self.edit_greetings_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_GREETINGS_TEXT))
        self.cbq_handler(self.act_edit_greetings_cooldown, lambda c: c.data == CBT.EDIT_GREETINGS_COOLDOWN)
        self.msg_handler(self.edit_greetings_cooldown, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_GREETINGS_COOLDOWN))
        self.cbq_handler(self.act_edit_order_confirm_reply_text, lambda c: c.data == CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT)
        self.msg_handler(self.edit_order_confirm_reply_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT))
        self.cbq_handler(self.act_edit_review_reply_text, lambda c: c.data.startswith(f"{CBT.EDIT_REVIEW_REPLY_TEXT}:"))
        self.msg_handler(self.edit_review_reply_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_REVIEW_REPLY_TEXT))
        self.msg_handler(self.manual_delivery_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.MANUAL_AD_TEST))
        self.msg_handler(self.act_ban, commands=["ban"])
        self.msg_handler(self.ban, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.BAN))
        self.msg_handler(self.act_unban, commands=["unban"])
        self.msg_handler(self.unban, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.UNBAN))
        self.msg_handler(self.send_ban_list, commands=["black_list"])
        self.msg_handler(self.act_edit_watermark, commands=["watermark"])
        self.msg_handler(self.edit_watermark, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_WATERMARK))
        self.msg_handler(self.send_logs, commands=["logs"])
        self.msg_handler(self.del_logs, commands=["del_logs"])
        self.msg_handler(self.about, commands=["about"])
        self.msg_handler(self.check_updates, commands=["check_updates"])
        self.msg_handler(self.update, commands=["update"])
        self.msg_handler(self.get_backup, commands=["get_backup"])
        self.msg_handler(self.create_backup, commands=["create_backup"])
        self.msg_handler(self.send_system_info, commands=["sys"])
        self.msg_handler(self.restart_cardinal, commands=["restart"])
        self.msg_handler(self.ask_power_off, commands=["power_off"])
        self.msg_handler(self.send_announcements_kb, commands=["announcements"]) # Если команда осталась
        self.cbq_handler(self.send_review_reply_text, lambda c: c.data.startswith(f"{CBT.SEND_REVIEW_REPLY_TEXT}:"))

        self.cbq_handler(self.act_send_funpay_message, lambda c: c.data.startswith(f"{CBT.SEND_FP_MESSAGE}:"))
        self.cbq_handler(self.open_reply_menu, lambda c: c.data.startswith(f"{CBT.BACK_TO_REPLY_KB}:"))
        self.cbq_handler(self.extend_new_message_notification, lambda c: c.data.startswith(f"{CBT.EXTEND_CHAT}:"))
        self.msg_handler(self.send_funpay_message, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.SEND_FP_MESSAGE))
        self.cbq_handler(self.ask_confirm_refund, lambda c: c.data.startswith(f"{CBT.REQUEST_REFUND}:"))
        self.cbq_handler(self.cancel_refund, lambda c: c.data.startswith(f"{CBT.REFUND_CANCELLED}:"))
        self.cbq_handler(self.refund, lambda c: c.data.startswith(f"{CBT.REFUND_CONFIRMED}:"))
        self.cbq_handler(self.open_order_menu, lambda c: c.data.startswith(f"{CBT.BACK_TO_ORDER_KB}:"))
        self.cbq_handler(self.open_cp, lambda c: c.data == CBT.MAIN)
        self.cbq_handler(self.open_cp2, lambda c: c.data == CBT.MAIN2)
        self.cbq_handler(self.open_settings_section, lambda c: c.data.startswith(f"{CBT.CATEGORY}:"))
        self.cbq_handler(self.switch_param, lambda c: c.data.startswith(f"{CBT.SWITCH}:"))
        self.cbq_handler(self.switch_chat_notification, lambda c: c.data.startswith(f"{CBT.SWITCH_TG_NOTIFICATIONS}:"))
        self.cbq_handler(self.power_off, lambda c: c.data.startswith(f"{CBT.SHUT_DOWN}:"))
        self.cbq_handler(self.cancel_power_off, lambda c: c.data == CBT.CANCEL_SHUTTING_DOWN)
        self.cbq_handler(self.cancel_action, lambda c: c.data == CBT.CLEAR_STATE)
        self.cbq_handler(self.send_old_mode_help_text, lambda c: c.data == CBT.OLD_MOD_HELP)
        self.cbq_handler(self.empty_callback, lambda c: c.data == CBT.EMPTY)
        self.cbq_handler(self.switch_lang, lambda c: c.data.startswith(f"{CBT.LANG}:"))

    def send_notification(self, text: str | None, keyboard: K | None = None,
                          notification_type: str = utils.NotificationTypes.other, photo: bytes | None = None,
                          pin: bool = False):
        kwargs = {}
        if keyboard is not None:
            kwargs["reply_markup"] = keyboard
        to_delete_chats = [] # Чаты, из которых бот был удален или заблокирован
        
        for chat_id_str in list(self.notification_settings.keys()): # list() для безопасного удаления во время итерации
            # Пропускаем, если уведомления данного типа выключены (кроме критических и важных объявлений)
            if notification_type not in [NotificationTypes.critical, NotificationTypes.important_announcement] and \
               not self.is_notification_enabled(chat_id_str, notification_type):
                continue
            # Для критических уведомлений дополнительно проверяем, авторизован ли кто-то в этом чате
            # (Это нужно, если логика __default_notification_settings изменится или для старых данных)
            if notification_type == NotificationTypes.critical:
                is_authorized_in_chat = any(uid in self.authorized_users for uid in self.user_states.get(int(chat_id_str), {}).keys())
                if not is_authorized_in_chat and int(chat_id_str) not in self.authorized_users: # Если это не личный чат админа
                    # Проверим, является ли этот чат одним из чатов админов (на случай если админ использует несколько чатов)
                    is_admin_chat = False
                    for admin_id in self.authorized_users:
                        # Предположим, что chat_id для личного чата равен user_id
                        if str(admin_id) == chat_id_str:
                            is_admin_chat = True
                            break
                    if not is_admin_chat:
                        continue


            try:
                if photo:
                    msg = self.bot.send_photo(chat_id_str, photo, caption=text, **kwargs) # caption для фото
                else:
                    msg = self.bot.send_message(chat_id_str, text, **kwargs)

                if notification_type == utils.NotificationTypes.bot_start:
                    self.init_messages.append((msg.chat.id, msg.id))

                if pin:
                    try: # Обертка для pin, так как может не быть прав
                        self.bot.pin_chat_message(msg.chat.id, msg.id, disable_notification=True) # disable_notification, чтобы не было второго уведомления
                    except Exception as pin_e:
                        logger.warning(f"Не удалось закрепить сообщение в чате {msg.chat.id}: {pin_e}")
            except Exception as e:
                logger.error(_("log_tg_notification_error", chat_id_str)) # Локализовано
                logger.debug("TRACEBACK", exc_info=True)
                # Обработка ошибок отправки (например, если бот заблокирован в чате)
                if isinstance(e, ApiTelegramException) and (
                        e.error_code == 403 or # Forbidden: bot was blocked by the user / kicked from group
                        (e.error_code == 400 and e.description in ("Bad Request: chat not found", 
                                                                  "Bad Request: group chat was upgraded to a supergroup chat"))):
                    to_delete_chats.append(chat_id_str)
                continue
                
        # Удаляем чаты, в которые не удалось отправить сообщение
        if to_delete_chats:
            for chat_id_del in to_delete_chats:
                if chat_id_del in self.notification_settings:
                    del self.notification_settings[chat_id_del]
            utils.save_notification_settings(self.notification_settings)


    def add_command_to_menu(self, command: str, help_text_key: str) -> None: # help_text_key - ключ для локализации
        self.commands[command] = help_text_key

    def setup_commands(self):
        # Команды устанавливаются для каждого языка отдельно
        for lang_code in [None] + list(localizer.languages.keys()): # None для языка по умолчанию
            try:
                # Описания команд берутся из локализации
                bot_commands = [BotCommand(f"/{cmd_key}", _(help_text_key, language=lang_code)) 
                                for cmd_key, help_text_key in self.commands.items()]
                self.bot.set_my_commands(bot_commands, language_code=lang_code)
            except Exception as e:
                logger.error(f"Не удалось установить команды для языка '{lang_code}': {e}")

    def edit_bot(self):
        # Изменение имени бота
        try:
            bot_me = self.bot.get_me()
            current_name = bot_me.full_name
            # Новое имя бота (можно оставить как есть или сделать более креативным)
            # Пока оставим FPCortex, но можно сделать, например, "FPCortex Ассистент"
            new_bot_name = "FPCortex" # Основное имя
            
            # Добавляем эмодзи или статус, если имя короткое
            name_suffix_options = [" 🚀", " | FunPay Bot", " ✨"]
            if len(new_bot_name) < 30: # Макс. длина имени бота 32 символа
                for suffix in name_suffix_options:
                    if len(new_bot_name) + len(suffix) <= 32:
                        new_bot_name += suffix
                        break
            
            if new_bot_name != current_name:
                 self.bot.set_my_name(new_bot_name)
                 logger.info(f"Имя бота изменено на: {new_bot_name}")
        except ApiTelegramException as e:
            logger.error(f"Не удалось изменить имя бота: {e}")

        # Изменение описания "О боте" и короткого описания
        # Ссылки убраны по требованию, так что описания будут без них
        
        # Короткое описание
        # new_short_description = _("adv_fpc") # "FPCortex - твой лучший ассистент для FunPay!"
        new_short_description = "🚀 Ваш надежный ассистент для FunPay!" # Пример более короткого
        try:
            current_short_desc_obj = self.bot.get_my_short_description()
            if current_short_desc_obj.short_description != new_short_description:
                self.bot.set_my_short_description(new_short_description)
                logger.info(f"Короткое описание бота изменено на: {new_short_description}")
        except ApiTelegramException as e:
            logger.error(f"Не удалось изменить короткое описание бота: {e}")

        # Полное описание "О боте"
        for lang_code in [None] + list(localizer.languages.keys()):
            # adv_description уже локализован и содержит версию
            new_full_description = _("adv_description", self.cortex.VERSION, language=lang_code)
            try:
                current_full_desc_obj = self.bot.get_my_description(language_code=lang_code)
                if current_full_desc_obj.description != new_full_description:
                    self.bot.set_my_description(new_full_description, language_code=lang_code)
                    logger.info(f"Полное описание бота для языка '{lang_code or 'default'}' изменено.")
            except ApiTelegramException as e:
                logger.error(f"Не удалось изменить полное описание бота для языка '{lang_code or 'default'}': {e}")


    def init(self):
        self.__register_handlers()
        # Устанавливаем команды и описания при инициализации
        self.setup_commands()
        self.edit_bot() 
        logger.info(_("log_tg_initialized")) # Локализовано

    def run(self):
        # bot_started уже локализован
        self.send_notification(_("bot_started"), notification_type=utils.NotificationTypes.bot_start)
        k_err_count = 0 # Переименовано для ясности
        while True:
            try:
                bot_username = self.bot.get_me().username
                logger.info(_("log_tg_started", bot_username)) # Локализовано
                self.bot.infinity_polling(logger_level=logging.WARNING) # Уровень логгирования для polling можно сделать WARN
            except Exception as e:
                k_err_count += 1
                # log_tg_update_error уже локализован
                logger.error(_("log_tg_update_error", k_err_count))
                logger.debug(f"Детали исключения polling: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(15) # Увеличена задержка перед рестартом polling