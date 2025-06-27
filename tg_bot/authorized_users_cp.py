# START OF FILE FunPayCortex-main/tg_bot/authorized_users_cp.py

"""
В данном модуле описаны функции для ПУ настроек авторизованных пользователей.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import telebot.apihelper

if TYPE_CHECKING:
    from cortex import Cortex
from tg_bot import keyboards as kb, CBT, utils
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_authorized_users_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def open_authorized_users_list(c: CallbackQuery):
        """
        Открывает список пользователей, авторизованных в ПУ.
        """
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_au"), c.message.chat.id, c.message.id,
                              reply_markup=kb.authorized_users(cortex_instance, offset, c.from_user.id))
        bot.answer_callback_query(c.id)

    def open_authorized_user_settings(c: CallbackQuery):
        """
        Открывает настройки конкретного пользователя.
        """
        __, user_id_str, offset_str = c.data.split(":")
        user_id = int(user_id_str)
        offset = int(offset_str)
        
        user_info = cortex_instance.telegram.authorized_users.get(user_id)
        if not user_info:
            bot.answer_callback_query(c.id, _("user_not_found"), show_alert=True)
            return

        user_display_name = user_info.get("username", str(user_id))
        user_role = user_info.get("role", "N/A")
        role_text = _(f"role_{user_role}")
        
        text_to_send = _("au_user_settings", f"<a href='tg:user?id={user_id}'>{telebot.util.escape(user_display_name)}</a> (ID: {user_id})\n<b>{_('user_role')}:</b> {role_text}")
        try:
            bot.edit_message_text(text_to_send, c.message.chat.id,
                                  c.message.id,
                                  reply_markup=kb.authorized_user_settings(cortex_instance, user_id, offset, True, c.from_user.id))
        except telebot.apihelper.ApiTelegramException:
            logger.warning(_("crd_tg_au_err", user_id))
            logger.debug("TRACEBACK", exc_info=True)
            bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id,
                                  reply_markup=kb.authorized_user_settings(cortex_instance, user_id, offset, False, c.from_user.id))

    def revoke_user_access(c: CallbackQuery, confirm: bool = False):
        """Отозвать доступ у пользователя."""
        __, user_id_str, offset_str = c.data.split(":")[:3]
        user_id_to_revoke = int(user_id_str)
        offset = int(offset_str)

        if not confirm:
            kb = InlineKeyboardMarkup().row(
                InlineKeyboardButton(f"✅ {_('gl_yes')}", callback_data=f"{CBT.REVOKE_USER_ACCESS}:{user_id_to_revoke}:{offset}:1"),
                InlineKeyboardButton(f"❌ {_('gl_no')}", callback_data=f"{CBT.AUTHORIZED_USER_SETTINGS}:{user_id_to_revoke}:{offset}")
            )
            bot.answer_callback_query(c.id, _("exit_from_cp_warning"), show_alert=True)
            bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=kb)
            return

        if user_id_to_revoke in tg.authorized_users:
            revoked_user_info = tg.authorized_users.pop(user_id_to_revoke)
            utils.save_authorized_users(tg.authorized_users)
            logger.warning(_("log_user_revoked", c.from_user.username, c.from_user.id, revoked_user_info.get("username", user_id_to_revoke), user_id_to_revoke))
            
            if c.from_user.id == user_id_to_revoke:
                bot.edit_message_text(_("exit_from_cp_success"), c.message.chat.id, c.message.id)
                bot.answer_callback_query(c.id, _("exit_from_cp_success_alert"), show_alert=True)
            else:
                bot.answer_callback_query(c.id, _("user_access_revoked", revoked_user_info.get("username", user_id_to_revoke)), show_alert=True)
                c.data = f"{CBT.AUTHORIZED_USERS}:{offset}"
                open_authorized_users_list(c)
        else:
            bot.answer_callback_query(c.id, _("user_not_found"), show_alert=True)
            c.data = f"{CBT.AUTHORIZED_USERS}:{offset}"
            open_authorized_users_list(c)

    def change_user_role(c: CallbackQuery):
        """Изменить роль пользователя."""
        __, user_id_str, offset_str, new_role = c.data.split(":")
        user_id_to_change = int(user_id_str)
        offset = int(offset_str)

        if user_id_to_change in tg.authorized_users:
            if new_role == "manager":
                admins = [uid for uid, uinfo in tg.authorized_users.items() if uinfo.get("role") == "admin"]
                if len(admins) <= 1 and tg.authorized_users[user_id_to_change].get("role") == "admin":
                    bot.answer_callback_query(c.id, _("demote_last_admin_error"), show_alert=True)
                    return

            tg.authorized_users[user_id_to_change]["role"] = new_role
            utils.save_authorized_users(tg.authorized_users)
            logger.warning(_("log_user_role_changed", c.from_user.username, c.from_user.id, tg.authorized_users[user_id_to_change].get("username", user_id_to_change), user_id_to_change, new_role))
            bot.answer_callback_query(c.id, _("user_role_changed_success", tg.authorized_users[user_id_to_change].get("username", user_id_to_change), _(f"role_{new_role}")), show_alert=True)

        c.data = f"{CBT.AUTHORIZED_USER_SETTINGS}:{user_id_to_change}:{offset}"
        open_authorized_user_settings(c)

    def open_manager_settings(c: CallbackQuery):
        """Открыть настройки для менеджеров."""
        key = cortex_instance.MAIN_CFG["Manager"].get("registration_key", "")
        key_text = f"<code>{utils.escape(key)}</code>" if key else _("manager_key_not_set")
        text = _("manager_settings_desc", key_text)
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(_("set_manager_key_btn"), callback_data=CBT.SET_MANAGER_KEY),
            InlineKeyboardButton(_("gl_back"), callback_data=f"{CBT.AUTHORIZED_USERS}:0")
        )
        bot.edit_message_text(text, c.message.chat.id, c.message.id, reply_markup=kb)
        bot.answer_callback_query(c.id)

    def act_set_manager_key(c: CallbackQuery):
        """Активировать ввод ключа регистрации менеджера."""
        result = bot.send_message(c.message.chat.id, _("enter_manager_key_prompt"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.SET_MANAGER_KEY)
        bot.answer_callback_query(c.id)

    def set_manager_key(m: Message):
        """Установить ключ регистрации менеджера."""
        tg.clear_state(m.chat.id, m.from_user.id, True)
        new_key = m.text.strip()
        cortex_instance.MAIN_CFG.set("Manager", "registration_key", new_key)
        cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        logger.warning(_("log_manager_key_changed", m.from_user.username, m.from_user.id, new_key))
        
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(_("gl_back"), callback_data=CBT.MANAGER_SETTINGS))
        bot.reply_to(m, _("manager_key_changed_success"), reply_markup=kb)

    def exit_cp(c: CallbackQuery):
        """Запросить подтверждение на выход из ПУ."""
        __, user_id_str, offset_str = c.data.split(":")
        user_id_to_exit = int(user_id_str)
        offset = int(offset_str)

        if c.from_user.id != user_id_to_exit:
            bot.answer_callback_query(c.id, _("admin_only_command"), show_alert=True)
            return

        kb = InlineKeyboardMarkup().row(
            InlineKeyboardButton(f"✅ {_('gl_yes')}", callback_data=f"{CBT.CONFIRM_EXIT_FROM_CP}:{user_id_to_exit}:{offset}"),
            InlineKeyboardButton(f"❌ {_('gl_no')}", callback_data=f"{CBT.AUTHORIZED_USERS}:{offset}")
        )
        bot.answer_callback_query(c.id, _("exit_from_cp_warning"), show_alert=True)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=kb)
    
    def confirm_exit_cp(c: CallbackQuery):
        """Подтверждение выхода из ПУ (отзыв доступа)."""
        __, user_id_str, offset_str = c.data.split(":")
        user_id_to_revoke = int(user_id_str)
        
        if c.from_user.id != user_id_to_revoke:
            bot.answer_callback_query(c.id, _("admin_only_command"), show_alert=True)
            return
            
        c.data = f"{CBT.REVOKE_USER_ACCESS}:{user_id_to_revoke}:{offset_str}:1"
        revoke_user_access(c, confirm=True)


    tg.cbq_handler(open_authorized_users_list, lambda c: c.data.startswith(f"{CBT.AUTHORIZED_USERS}:"))
    tg.cbq_handler(open_authorized_user_settings, lambda c: c.data.startswith(f"{CBT.AUTHORIZED_USER_SETTINGS}:"))
    tg.cbq_handler(lambda c: revoke_user_access(c, confirm=False), lambda c: c.data.startswith(f"{CBT.REVOKE_USER_ACCESS}:") and len(c.data.split(":")) == 3)
    tg.cbq_handler(lambda c: revoke_user_access(c, confirm=True), lambda c: c.data.startswith(f"{CBT.REVOKE_USER_ACCESS}:") and len(c.data.split(":")) == 4)
    tg.cbq_handler(change_user_role, lambda c: c.data.startswith(f"{CBT.CHANGE_USER_ROLE}:"))
    tg.cbq_handler(open_manager_settings, lambda c: c.data == CBT.MANAGER_SETTINGS)
    tg.cbq_handler(act_set_manager_key, lambda c: c.data == CBT.SET_MANAGER_KEY)
    tg.msg_handler(set_manager_key, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.SET_MANAGER_KEY))
    tg.cbq_handler(exit_cp, lambda c: c.data.startswith(f"{CBT.EXIT_FROM_CP}:"))
    tg.cbq_handler(confirm_exit_cp, lambda c: c.data.startswith(f"{CBT.CONFIRM_EXIT_FROM_CP}:"))


BIND_TO_PRE_INIT = [init_authorized_users_cp]