# START OF FILE FunPayCortex/tg_bot/auto_response_cp.py

"""
В данном модуле описаны функции для ПУ конфига автоответчика.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from tg_bot import utils, keyboards, CBT, MENU_CFG
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery
from tg_bot.static_keyboards import CLEAR_STATE_BTN
import datetime
import logging

from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_auto_response_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def check_command_exists(command_index: int, message_obj: Message | CallbackQuery, reply_mode: bool = True) -> bool:
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id
        
        if command_index >= len(cortex_instance.RAW_AR_CFG.sections()):
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.CMD_LIST}:0"))
            text_error = _("ar_cmd_not_found_err", command_index)
            if reply_mode and isinstance(message_obj, Message):
                bot.reply_to(message_obj, text_error, reply_markup=update_button)
            else:
                bot.edit_message_text(text_error, chat_id, message_id, reply_markup=update_button)
            return False
        return True

    def open_commands_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_ar_list"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.commands_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    def act_add_command(c: CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("ar_enter_new_cmd"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.ADD_CMD)
        bot.answer_callback_query(c.id)

    def add_command(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        raw_command_input = m.text.strip().lower()
        commands_list_from_input = [cmd.strip() for cmd in raw_command_input.split("|") if cmd.strip()]

        error_keyboard = K().row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:ar"),
                                 B(_("ar_add_another"), callback_data=CBT.ADD_CMD))

        if not commands_list_from_input:
            bot.reply_to(m, _("ar_no_valid_commands_entered"), reply_markup=error_keyboard)
            return

        if len(commands_list_from_input) != len(set(commands_list_from_input)):
            seen_cmds = set()
            first_duplicate_cmd = ""
            for cmd_item in commands_list_from_input:
                if cmd_item in seen_cmds:
                    first_duplicate_cmd = cmd_item
                    break
                seen_cmds.add(cmd_item)
            bot.reply_to(m, _("ar_subcmd_duplicate_err", utils.escape(first_duplicate_cmd)), reply_markup=error_keyboard)
            return
        
        for new_cmd_item in commands_list_from_input:
            if new_cmd_item in cortex_instance.AR_CFG.sections():
                bot.reply_to(m, _("ar_cmd_already_exists_err", utils.escape(new_cmd_item)), reply_markup=error_keyboard)
                return
        
        raw_command_for_cfg = "|".join(commands_list_from_input)
        
        default_response_text = _("ar_default_response_text")
        
        cortex_instance.RAW_AR_CFG.add_section(raw_command_for_cfg)
        cortex_instance.RAW_AR_CFG.set(raw_command_for_cfg, "response", default_response_text)
        cortex_instance.RAW_AR_CFG.set(raw_command_for_cfg, "telegramNotification", "0")

        for cmd_in_set in commands_list_from_input:
            cortex_instance.AR_CFG.add_section(cmd_in_set)
            cortex_instance.AR_CFG.set(cmd_in_set, "response", default_response_text)
            cortex_instance.AR_CFG.set(cmd_in_set, "telegramNotification", "0")
            cortex_instance.AR_CFG.set(cmd_in_set, "_raw_command_set", raw_command_for_cfg)


        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")

        all_raw_command_sets = cortex_instance.RAW_AR_CFG.sections()
        try:
            new_command_set_index = all_raw_command_sets.index(raw_command_for_cfg)
        except ValueError:
            logger.error(f"Не удалось найти добавленный сет команд '{raw_command_for_cfg}' в RAW_AR_CFG")
            new_command_set_index = len(all_raw_command_sets) -1

        offset_for_kb = utils.get_offset(new_command_set_index, MENU_CFG.AR_BTNS_AMOUNT)
        keyboard_success = K().row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:ar"),
                                   B(_("ar_add_more"), callback_data=CBT.ADD_CMD),
                                   B(_("gl_configure"), callback_data=f"{CBT.EDIT_CMD}:{new_command_set_index}:{offset_for_kb}"))
        logger.info(_("log_ar_added", m.from_user.username, m.from_user.id, raw_command_for_cfg))
        bot.reply_to(m, _("ar_cmd_added", utils.escape(raw_command_for_cfg)), reply_markup=keyboard_success)

    def open_edit_command_cp(c: CallbackQuery):
        split_data = c.data.split(":")
        command_set_index, offset = int(split_data[1]), int(split_data[2])
        if not check_command_exists(command_set_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        command_set_raw_text = cortex_instance.RAW_AR_CFG.sections()[command_set_index]
        command_set_obj = cortex_instance.RAW_AR_CFG[command_set_raw_text]
        
        keyboard_edit = keyboards.edit_command(cortex_instance, command_set_index, offset)

        default_notification_text = _("ar_default_notification_text")
        notification_text_from_cfg = command_set_obj.get("notificationText", default_notification_text)
        
        display_command_set = utils.escape(command_set_raw_text)
        display_response = utils.escape(command_set_obj.get("response", ""))
        display_notification_text = utils.escape(notification_text_from_cfg)

        message_text = f"""🛠️ <b>Редактирование команды/сета:</b>
<code>{display_command_set}</code>

📝 <b><i>{_('ar_response_text')}:</i></b>
<code>{display_response}</code>

🔔 <b><i>{_('ar_notification_text')}:</i></b>
<code>{display_notification_text}</code>

⏱️ <i>{_('gl_last_update')}:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"""
        bot.edit_message_text(message_text, c.message.chat.id, c.message.id, reply_markup=keyboard_edit)
        bot.answer_callback_query(c.id)

    def act_edit_command_response(c: CallbackQuery):
        split_data = c.data.split(":")
        command_set_index, offset = int(split_data[1]), int(split_data[2])

        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_message_text", "v_chat_id", "v_chat_name", "v_photo", "v_sleep"]
        text_to_send = f"{_('v_edit_response_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)

        result = bot.send_message(c.message.chat.id, text_to_send, reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.EDIT_CMD_RESPONSE_TEXT,
                     {"command_index": command_set_index, "offset": offset})
        bot.answer_callback_query(c.id)

    def edit_command_response(m: Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)["data"]
        command_set_index = state_data["command_index"]
        offset = state_data["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_command_exists(command_set_index, m):
            return

        new_response_text = m.text.strip()
        command_set_raw_text = cortex_instance.RAW_AR_CFG.sections()[command_set_index]
        
        cortex_instance.RAW_AR_CFG.set(command_set_raw_text, "response", new_response_text)
        
        commands_in_set = [cmd.strip() for cmd in command_set_raw_text.split("|") if cmd.strip()]
        for cmd_item in commands_in_set:
            if cmd_item in cortex_instance.AR_CFG.sections():
                cortex_instance.AR_CFG.set(cmd_item, "response", new_response_text)
            
        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")

        logger.info(_("log_ar_response_text_changed", m.from_user.username, m.from_user.id, command_set_raw_text, new_response_text))
        keyboard_reply = K().row(B(_("gl_back"), callback_data=f"{CBT.EDIT_CMD}:{command_set_index}:{offset}"),
                                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_CMD_RESPONSE_TEXT}:{command_set_index}:{offset}"))
        bot.reply_to(m, _("ar_response_text_changed", utils.escape(command_set_raw_text), utils.escape(new_response_text)),
                     reply_markup=keyboard_reply)

    def act_edit_command_notification(c: CallbackQuery):
        split_data = c.data.split(":")
        command_set_index, offset = int(split_data[1]), int(split_data[2])

        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_message_text", "v_chat_id", "v_chat_name"]
        text_to_send = f"{_('v_edit_notification_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)

        result = bot.send_message(c.message.chat.id, text_to_send, reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.EDIT_CMD_NOTIFICATION_TEXT,
                     {"command_index": command_set_index, "offset": offset})
        bot.answer_callback_query(c.id)

    def edit_command_notification(m: Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)["data"]
        command_set_index = state_data["command_index"]
        offset = state_data["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)

        if not check_command_exists(command_set_index, m):
            return

        new_notification_text = m.text.strip()
        command_set_raw_text = cortex_instance.RAW_AR_CFG.sections()[command_set_index]
        
        cortex_instance.RAW_AR_CFG.set(command_set_raw_text, "notificationText", new_notification_text)
        
        commands_in_set = [cmd.strip() for cmd in command_set_raw_text.split("|") if cmd.strip()]
        for cmd_item in commands_in_set:
            if cmd_item in cortex_instance.AR_CFG.sections():
                cortex_instance.AR_CFG.set(cmd_item, "notificationText", new_notification_text)
                
        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")

        logger.info(
            _("log_ar_notification_text_changed", m.from_user.username, m.from_user.id, command_set_raw_text, new_notification_text))
        keyboard_reply = K().row(B(_("gl_back"), callback_data=f"{CBT.EDIT_CMD}:{command_set_index}:{offset}"),
                                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_CMD_NOTIFICATION_TEXT}:{command_set_index}:{offset}"))
        bot.reply_to(m, _("ar_notification_text_changed", utils.escape(command_set_raw_text), utils.escape(new_notification_text)),
                     reply_markup=keyboard_reply)

    def switch_notification(c: CallbackQuery):
        split_data = c.data.split(":")
        command_set_index, offset = int(split_data[1]), int(split_data[2])
        
        if not check_command_exists(command_set_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        command_set_raw_text = cortex_instance.RAW_AR_CFG.sections()[command_set_index]
        command_set_obj = cortex_instance.RAW_AR_CFG[command_set_raw_text]
        
        current_notif_status_str = command_set_obj.get("telegramNotification", "0")
        new_notif_status_str = "0" if current_notif_status_str == "1" else "1"
        
        cortex_instance.RAW_AR_CFG.set(command_set_raw_text, "telegramNotification", new_notif_status_str)
        
        commands_in_set = [cmd.strip() for cmd in command_set_raw_text.split("|") if cmd.strip()]
        for cmd_item in commands_in_set:
            if cmd_item in cortex_instance.AR_CFG.sections():
                cortex_instance.AR_CFG.set(cmd_item, "telegramNotification", new_notif_status_str)
                
        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")
        logger.info(_("log_param_changed", c.from_user.username, c.from_user.id, "telegramNotification", command_set_raw_text, new_notif_status_str))
        
        c.data = f"{CBT.EDIT_CMD}:{command_set_index}:{offset}"
        open_edit_command_cp(c)

    def del_command(c: CallbackQuery):
        split_data = c.data.split(":")
        command_set_index, offset = int(split_data[1]), int(split_data[2])
        if not check_command_exists(command_set_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        command_set_to_delete = cortex_instance.RAW_AR_CFG.sections()[command_set_index]
        
        cortex_instance.RAW_AR_CFG.remove_section(command_set_to_delete)
        
        commands_in_set_to_delete = [cmd.strip() for cmd in command_set_to_delete.split("|") if cmd.strip()]
        for cmd_item_to_delete in commands_in_set_to_delete:
            if cortex_instance.AR_CFG.has_section(cmd_item_to_delete):
                cortex_instance.AR_CFG.remove_section(cmd_item_to_delete)
                
        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")
        logger.info(_("log_ar_cmd_deleted", c.from_user.username, c.from_user.id, command_set_to_delete))
        
        new_offset = max(0, offset - MENU_CFG.AR_BTNS_AMOUNT if offset >= MENU_CFG.AR_BTNS_AMOUNT and len(cortex_instance.RAW_AR_CFG.sections()) < offset + MENU_CFG.AR_BTNS_AMOUNT else offset)
        new_offset = 0 if len(cortex_instance.RAW_AR_CFG.sections()) <= MENU_CFG.AR_BTNS_AMOUNT else new_offset

        bot.edit_message_text(_("desc_ar_list"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.commands_list(cortex_instance, new_offset))
        bot.answer_callback_query(c.id, _("ar_command_deleted_successfully", command_name=utils.escape(command_set_to_delete)), show_alert=True)

    tg.cbq_handler(open_commands_list, lambda c: c.data.startswith(f"{CBT.CMD_LIST}:"))
    tg.cbq_handler(act_add_command, lambda c: c.data == CBT.ADD_CMD)
    tg.msg_handler(add_command, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.ADD_CMD))
    tg.cbq_handler(open_edit_command_cp, lambda c: c.data.startswith(f"{CBT.EDIT_CMD}:"))
    tg.cbq_handler(act_edit_command_response, lambda c: c.data.startswith(f"{CBT.EDIT_CMD_RESPONSE_TEXT}:"))
    tg.msg_handler(edit_command_response,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.EDIT_CMD_RESPONSE_TEXT))
    tg.cbq_handler(act_edit_command_notification, lambda c: c.data.startswith(f"{CBT.EDIT_CMD_NOTIFICATION_TEXT}:"))
    tg.msg_handler(edit_command_notification,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.EDIT_CMD_NOTIFICATION_TEXT))
    tg.cbq_handler(switch_notification, lambda c: c.data.startswith(f"{CBT.SWITCH_CMD_NOTIFICATION}:"))
    tg.cbq_handler(del_command, lambda c: c.data.startswith(f"{CBT.DEL_CMD}:"))


BIND_TO_PRE_INIT = [init_auto_response_cp]

# END OF FILE FunPayCortex/tg_bot/auto_response_cp.py