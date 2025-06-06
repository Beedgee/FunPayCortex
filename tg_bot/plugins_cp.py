# START OF FILE FunPayCortex/tg_bot/plugins_cp.py

"""
В данном модуле описаны функции для ПУ плагинами.
Модуль реализован в виде плагина.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from locales.localizer import Localizer

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery
import datetime
import logging

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_plugins_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def check_plugin_exists(uuid_to_check: str, message_obj: Message | CallbackQuery) -> bool:
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id

        if uuid_to_check not in cortex_instance.plugins:
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.PLUGINS_LIST}:0"))
            bot.edit_message_text(_("pl_not_found_err", utils.escape(uuid_to_check)), chat_id, message_id,
                                  reply_markup=update_button)
            return False
        return True

    def open_plugins_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        plugins_channel_link = "https://t.me/FunPayCortex"
        desc_plugins_text = _("desc_pl") + f"\n\n🔗 <b>{_('pl_safe_source')}:</b> <a href=\"{plugins_channel_link}\">{_('pl_channel_button')}</a>"

        bot.edit_message_text(desc_plugins_text, c.message.chat.id, c.message.id,
                              reply_markup=keyboards.plugins_list(cortex_instance, offset),
                              disable_web_page_preview=True)
        bot.answer_callback_query(c.id)

    def open_edit_plugin_cp(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return

        plugin_obj = cortex_instance.plugins[plugin_uuid]
        status_text = _("pl_status_active") if plugin_obj.enabled else _("pl_status_inactive")

        text_to_send = f"""🧩 <b>{utils.escape(plugin_obj.name)} v{utils.escape(plugin_obj.version)}</b>
{status_text}

📝 <i>{utils.escape(plugin_obj.description)}</i>

🆔 <b>UUID:</b> <code>{utils.escape(plugin_obj.uuid)}</code>
👨‍💻 <b>{_('pl_author')}:</b> {utils.escape(plugin_obj.credits)}

⏱️ <i>{_('gl_last_update')}:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"""

        keyboard_to_send = keyboards.edit_plugin(cortex_instance, plugin_uuid, offset)

        bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id, reply_markup=keyboard_to_send)
        bot.answer_callback_query(c.id)

    def open_plugin_commands(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return

        plugin_obj = cortex_instance.plugins[plugin_uuid]

        if not plugin_obj.commands:
            bot.answer_callback_query(c.id, _("pl_no_commands"), show_alert=True)
            return

        commands_text_list = []
        for cmd_key, help_text_key_in_plugin in plugin_obj.commands.items():
            translated_help = localizer.plugin_translate(plugin_obj.uuid, help_text_key_in_plugin)
            if translated_help == f"{plugin_obj.uuid}_{help_text_key_in_plugin}" or translated_help == help_text_key_in_plugin:
                 final_help_text = _(help_text_key_in_plugin)
            else:
                 final_help_text = translated_help
            commands_text_list.append(f"<code>/{utils.escape(cmd_key)}</code> - {utils.escape(final_help_text)}")

        commands_display_text = "\n\n".join(commands_text_list)
        text_to_send = f"{_('pl_commands_list', utils.escape(plugin_obj.name))}\n\n{commands_display_text}"
        keyboard_reply = K().add(B(_("gl_back"), callback_data=f"{CBT.EDIT_PLUGIN}:{plugin_uuid}:{offset}"))

        bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id, reply_markup=keyboard_reply)
        bot.answer_callback_query(c.id)


    def toggle_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return

        cortex_instance.toggle_plugin(plugin_uuid)

        plugin_name = cortex_instance.plugins[plugin_uuid].name
        log_message_key = "log_pl_activated" if cortex_instance.plugins[plugin_uuid].enabled else "log_pl_deactivated"
        logger.info(_(log_message_key, c.from_user.username, c.from_user.id, plugin_name))

        c.data = f"{CBT.EDIT_PLUGIN}:{plugin_uuid}:{offset}"
        open_edit_plugin_cp(c)

    def ask_delete_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.edit_plugin(cortex_instance, plugin_uuid, offset, ask_to_delete=True))
        bot.answer_callback_query(c.id)

    def cancel_delete_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.edit_plugin(cortex_instance, plugin_uuid, offset, ask_to_delete=False))
        bot.answer_callback_query(c.id)

    def delete_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c):
            bot.answer_callback_query(c.id)
            return

        plugin_to_delete = cortex_instance.plugins.get(plugin_uuid)
        if not plugin_to_delete:
            bot.answer_callback_query(c.id, _("pl_not_found_err", utils.escape(plugin_uuid)), show_alert=True)
            return

        plugin_path_to_delete = plugin_to_delete.path
        plugin_name_for_log_and_msg = plugin_to_delete.name

        if not os.path.exists(plugin_path_to_delete):
            bot.answer_callback_query(c.id, _("pl_file_not_found_err", utils.escape(plugin_path_to_delete)),
                                      show_alert=True)
            if plugin_uuid in cortex_instance.plugins:
                cortex_instance.plugins.pop(plugin_uuid)
            c.data = f"{CBT.PLUGINS_LIST}:{offset}"
            open_plugins_list(c)
            return

        if plugin_to_delete.delete_handler:
            try:
                plugin_to_delete.delete_handler(cortex_instance, c)
            except Exception as e:
                logger.error(_("log_pl_delete_handler_err", plugin_name_for_log_and_msg))
                logger.debug(f"Ошибка в delete_handler плагина {plugin_name_for_log_and_msg}: {e}", exc_info=True)
                bot.answer_callback_query(c.id, _("pl_delete_handler_failed", plugin_name=utils.escape(plugin_name_for_log_and_msg)), show_alert=True)

        try:
            os.remove(plugin_path_to_delete)
            logger.info(_("log_pl_deleted", c.from_user.username, c.from_user.id, plugin_name_for_log_and_msg))
            if plugin_uuid in cortex_instance.plugins:
                cortex_instance.plugins.pop(plugin_uuid)

            all_plugins_after_delete = list(sorted(cortex_instance.plugins.keys(), key=lambda x_uuid: cortex_instance.plugins[x_uuid].name.lower()))
            new_offset = max(0, offset - MENU_CFG.PLUGINS_BTNS_AMOUNT if offset >= MENU_CFG.PLUGINS_BTNS_AMOUNT and len(all_plugins_after_delete) < offset + MENU_CFG.PLUGINS_BTNS_AMOUNT else offset)
            new_offset = 0 if len(all_plugins_after_delete) <= MENU_CFG.PLUGINS_BTNS_AMOUNT else new_offset

            c.data = f"{CBT.PLUGINS_LIST}:{new_offset}"
            open_plugins_list(c)
            bot.answer_callback_query(c.id, _("pl_deleted_successfully", plugin_name=utils.escape(plugin_name_for_log_and_msg)), show_alert=True)
        except OSError as e:
            logger.error(f"Не удалось удалить файл плагина {plugin_path_to_delete}: {e}")
            bot.answer_callback_query(c.id, _("pl_file_delete_error", plugin_path=utils.escape(plugin_path_to_delete)) + f" (OS Error: {e.strerror})", show_alert=True)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при удалении плагина {plugin_path_to_delete}: {e}", exc_info=True)
            bot.answer_callback_query(c.id, _("pl_file_delete_error", plugin_path=utils.escape(plugin_path_to_delete)), show_alert=True)


    def act_upload_plugin(obj: CallbackQuery | Message):
        text_prompt = _("pl_new")

        if isinstance(obj, CallbackQuery):
            offset = int(obj.data.split(":")[1])
            result = bot.send_message(obj.message.chat.id, text_prompt, reply_markup=CLEAR_STATE_BTN())
            tg.set_state(obj.message.chat.id, result.id, obj.from_user.id, CBT.UPLOAD_PLUGIN, {"offset": offset})
            bot.answer_callback_query(obj.id)
        elif isinstance(obj, Message):
            result = bot.send_message(obj.chat.id, text_prompt, reply_markup=CLEAR_STATE_BTN())
            tg.set_state(obj.chat.id, result.id, obj.from_user.id, CBT.UPLOAD_PLUGIN, {"offset": 0})

    tg.cbq_handler(open_plugins_list, lambda c: c.data.startswith(f"{CBT.PLUGINS_LIST}:"))
    tg.cbq_handler(open_edit_plugin_cp, lambda c: c.data.startswith(f"{CBT.EDIT_PLUGIN}:"))
    tg.cbq_handler(open_plugin_commands, lambda c: c.data.startswith(f"{CBT.PLUGIN_COMMANDS}:"))
    tg.cbq_handler(toggle_plugin, lambda c: c.data.startswith(f"{CBT.TOGGLE_PLUGIN}:"))
    tg.cbq_handler(ask_delete_plugin, lambda c: c.data.startswith(f"{CBT.DELETE_PLUGIN}:"))
    tg.cbq_handler(cancel_delete_plugin, lambda c: c.data.startswith(f"{CBT.CANCEL_DELETE_PLUGIN}:"))
    tg.cbq_handler(delete_plugin, lambda c: c.data.startswith(f"{CBT.CONFIRM_DELETE_PLUGIN}:"))
    tg.cbq_handler(act_upload_plugin, lambda c: c.data.startswith(f"{CBT.UPLOAD_PLUGIN}:"))
    tg.msg_handler(act_upload_plugin, commands=["upload_plugin"])


BIND_TO_PRE_INIT = [init_plugins_cp]

# END OF FILE FunPayCortex/tg_bot/plugins_cp.py