# START OF FILE FunPayCortex-main/tg_bot/accounts_cp.py
from __future__ import annotations
from typing import TYPE_CHECKING
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

def init_accounts_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def open_accounts_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("acc_list_header"), c.message.chat.id, c.message.id,
                              reply_markup=kb.accounts_list(cortex_instance, offset, c.from_user.id))
        bot.answer_callback_query(c.id)

    def select_active_account(c: CallbackQuery):
        account_name = c.data.split(":")[1]
        if account_name not in cortex_instance.accounts:
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)
            return
        tg.active_account_for_user[c.from_user.id] = account_name
        bot.answer_callback_query(c.id, _("acc_selected_success", name=account_name), show_alert=True)
        c.data = f"{CBT.ACCOUNTS_LIST}:0"
        open_accounts_list(c)

    def toggle_account_status(c: CallbackQuery):
        account_name = c.data.split(":")[1]
        if account_name not in cortex_instance.FP_ACCOUNTS_CFG:
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)
            return
        
        current_status = cortex_instance.FP_ACCOUNTS_CFG[account_name]["enabled"]
        new_status = not current_status
        cortex_instance.MAIN_CFG.set(f"FunPayAccount_{account_name}", "enabled", "1" if new_status else "0")
        cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        cortex_instance.FP_ACCOUNTS_CFG[account_name]["enabled"] = new_status
        
        alert_text = _("acc_toggled_on", name=account_name) if new_status else _("acc_toggled_off", name=account_name)
        bot.answer_callback_query(c.id, alert_text, show_alert=True)
        c.data = f"{CBT.ACCOUNTS_LIST}:0"
        open_accounts_list(c)

    def ask_delete_account(c: CallbackQuery):
        account_name = c.data.split(":")[1]
        if account_name not in cortex_instance.FP_ACCOUNTS_CFG:
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)
            return
        
        kb = InlineKeyboardMarkup().row(
            InlineKeyboardButton(f"✅ {_('gl_yes')}", callback_data=f"{CBT.CONFIRM_DELETE_ACCOUNT}:{account_name}"),
            InlineKeyboardButton(f"❌ {_('gl_no')}", callback_data=f"{CBT.ACCOUNTS_LIST}:0")
        )
        bot.answer_callback_query(c.id, _("acc_delete_confirm", name=account_name), show_alert=True)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=kb)

    def confirm_delete_account(c: CallbackQuery):
        account_name = c.data.split(":")[1]
        if account_name not in cortex_instance.FP_ACCOUNTS_CFG:
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)
            return
        
        # Удаляем из конфига
        cortex_instance.MAIN_CFG.remove_option("FunPayAccounts", account_name)
        cortex_instance.MAIN_CFG.remove_section(f"FunPayAccount_{account_name}")
        cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        
        # Удаляем из рантайм-переменных
        cortex_instance.FP_ACCOUNTS_CFG.pop(account_name, None)
        cortex_instance.accounts.pop(account_name, None)
        
        bot.answer_callback_query(c.id, _("acc_deleted_success", name=account_name), show_alert=True)
        c.data = f"{CBT.ACCOUNTS_LIST}:0"
        open_accounts_list(c)

    def act_add_account_name(c: CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("acc_prompt_name"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "add_account_name")
        bot.answer_callback_query(c.id)

    def add_account_name(m: Message):
        account_name = m.text.strip()
        if account_name in cortex_instance.FP_ACCOUNTS_CFG:
            bot.reply_to(m, _("acc_err_name_exists"))
            return
        tg.clear_state(m.chat.id, m.from_user.id, True)
        result = bot.send_message(m.chat.id, _("acc_prompt_token", name=account_name), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(m.chat.id, result.id, m.from_user.id, "add_account_token", {"name": account_name})

    def add_account_token(m: Message):
        account_name = tg.get_state(m.chat.id, m.from_user.id)["data"]["name"]
        golden_key = m.text.strip()
        
        if len(golden_key) != 32:
            bot.reply_to(m, _("acc_err_token_invalid"))
            return
            
        tg.clear_state(m.chat.id, m.from_user.id, True)
        
        cortex_instance.MAIN_CFG.set("FunPayAccounts", account_name, "")
        cortex_instance.MAIN_CFG[f"FunPayAccount_{account_name}"] = {
            "golden_key": golden_key,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "enabled": "1"
        }
        cortex_instance.save_config(cortex_instance.MAIN_CFG, "configs/_main.cfg")
        cortex_instance.FP_ACCOUNTS_CFG[account_name] = {"enabled": True} # Add to runtime immediately
        
        bot.send_message(m.chat.id, _("acc_add_success", name=account_name))
        
        # Возвращаемся к списку аккаунтов
        msg = bot.send_message(m.chat.id, "...") # Placeholder message
        # ИЗМЕНЕНИЕ ЗДЕСЬ: Добавлен аргумент json_string='{}'
        c = CallbackQuery(id="0", from_user=m.from_user, chat_instance="", data=f"{CBT.ACCOUNTS_LIST}:0", message=msg, json_string='{}')
        open_accounts_list(c)


    tg.cbq_handler(open_accounts_list, lambda c: c.data.startswith(f"{CBT.ACCOUNTS_LIST}:"))
    tg.cbq_handler(select_active_account, lambda c: c.data.startswith(f"{CBT.SELECT_ACCOUNT}:"))
    tg.cbq_handler(toggle_account_status, lambda c: c.data.startswith(f"{CBT.TOGGLE_ACCOUNT}:"))
    tg.cbq_handler(ask_delete_account, lambda c: c.data.startswith(f"{CBT.DELETE_ACCOUNT}:"))
    tg.cbq_handler(confirm_delete_account, lambda c: c.data.startswith(f"{CBT.CONFIRM_DELETE_ACCOUNT}:"))
    tg.cbq_handler(act_add_account_name, lambda c: c.data == CBT.ADD_ACCOUNT)
    tg.msg_handler(add_account_name, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, "add_account_name"))
    tg.msg_handler(add_account_token, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, "add_account_token"))

BIND_TO_PRE_INIT = [init_accounts_cp]
# END OF FILE FunPayCortex-main/tg_bot/accounts_cp.py