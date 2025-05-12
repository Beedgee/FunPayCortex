"""
В данном модуле описаны функции для ПУ плагинами.
Модуль реализован в виде плагина.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cortex # Renamed FPCortex to Cortex

from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN # Используется для отмены действия
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
        # pl_not_found_err, gl_refresh уже локализованы
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id
        
        if uuid_to_check not in cortex_instance.plugins:
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.PLUGINS_LIST}:0"))
            # Используем utils.escape для UUID в сообщении об ошибке
            bot.edit_message_text(_("pl_not_found_err", utils.escape(uuid_to_check)), chat_id, message_id,
                                  reply_markup=update_button)
            return False
        return True

    def open_plugins_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        # desc_pl уже локализован
        bot.edit_message_text(_("desc_pl"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.plugins_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    def open_edit_plugin_cp(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        plugin_obj = cortex_instance.plugins[plugin_uuid]
        # pl_author, gl_last_update уже локализованы
        # Добавим ключ pl_status_active = "Статус: Активен 🚀" и pl_status_inactive = "Статус: Неактивен 💤"
        status_text = _("pl_status_active") if plugin_obj.enabled else _("pl_status_inactive")
        
        text_to_send = f"""🧩 <b>{utils.escape(plugin_obj.name)} v{utils.escape(plugin_obj.version)}</b>
{status_text}

📝 <i>{utils.escape(plugin_obj.description)}</i>

🆔 <b>UUID:</b> <code>{utils.escape(plugin_obj.uuid)}</code>
👨‍💻 <b>{_('pl_author')}:</b> {utils.escape(plugin_obj.credits)}

⏱️ <i>{_('gl_last_update')}:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>""" # Полная дата

        keyboard_to_send = keyboards.edit_plugin(cortex_instance, plugin_uuid, offset) # Клавиатура уже обновлена

        bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id, reply_markup=keyboard_to_send)
        bot.answer_callback_query(c.id)

    def open_plugin_commands(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        plugin_obj = cortex_instance.plugins[plugin_uuid]
        
        if not plugin_obj.commands: # Если у плагина нет команд
            # Добавим ключ pl_no_commands = "У этого плагина нет зарегистрированных команд."
            bot.answer_callback_query(c.id, _("pl_no_commands", language=localizer.current_language), show_alert=True)
            return

        commands_text_list = []
        for cmd_key, help_text_key_in_plugin in plugin_obj.commands.items():
            # Пытаемся получить перевод описания команды плагина
            # Сначала ищем ключ вида UUID_help_text_key, потом просто help_text_key
            translated_help = localizer.plugin_translate(plugin_obj.uuid, help_text_key_in_plugin)
            # Если перевод не нашелся, используем ключ как есть (возможно, он уже на нужном языке)
            if translated_help == f"{plugin_obj.uuid}_{help_text_key_in_plugin}" or translated_help == help_text_key_in_plugin:
                 final_help_text = help_text_key_in_plugin # или _(help_text_key_in_plugin, language=localizer.current_language) если ключи общие
            else:
                 final_help_text = translated_help

            commands_text_list.append(f"<code>/{utils.escape(cmd_key)}</code> - {utils.escape(final_help_text)}")

        commands_display_text = "\n\n".join(commands_text_list)
        # pl_commands_list уже локализован
        text_to_send = f"{_('pl_commands_list', utils.escape(plugin_obj.name))}\n\n{commands_display_text}"
        # gl_back уже локализован
        keyboard_reply = K().add(B(_("gl_back"), callback_data=f"{CBT.EDIT_PLUGIN}:{plugin_uuid}:{offset}"))

        bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id, reply_markup=keyboard_reply)
        bot.answer_callback_query(c.id)


    def toggle_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        cortex_instance.toggle_plugin(plugin_uuid) # Метод сам меняет состояние enabled
        
        plugin_name = cortex_instance.plugins[plugin_uuid].name
        # log_pl_activated, log_pl_deactivated уже локализованы
        log_message_key = "log_pl_activated" if cortex_instance.plugins[plugin_uuid].enabled else "log_pl_deactivated"
        logger.info(_(log_message_key, c.from_user.username, c.from_user.id, plugin_name))
        
        # Обновляем сообщение с информацией о плагине
        c.data = f"{CBT.EDIT_PLUGIN}:{plugin_uuid}:{offset}" 
        open_edit_plugin_cp(c) # Эта функция сама ответит на колбэк

    def ask_delete_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return
        # Клавиатура keyboards.edit_plugin уже обновлена для отображения подтверждения
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.edit_plugin(cortex_instance, plugin_uuid, offset, ask_to_delete=True))
        bot.answer_callback_query(c.id)

    def cancel_delete_plugin(c: CallbackQuery): # Эта функция вызывается при нажатии "Нет" на подтверждении удаления
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return
        # Возвращаем обычную клавиатуру редактирования плагина
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.edit_plugin(cortex_instance, plugin_uuid, offset, ask_to_delete=False))
        bot.answer_callback_query(c.id)

    def delete_plugin(c: CallbackQuery):
        split_data = c.data.split(":")
        plugin_uuid, offset_str = split_data[1], split_data[2]
        offset = int(offset_str)

        if not check_plugin_exists(plugin_uuid, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        plugin_to_delete = cortex_instance.plugins.get(plugin_uuid) # Получаем объект плагина перед удалением
        if not plugin_to_delete: # Дополнительная проверка
            bot.answer_callback_query(c.id, _("pl_not_found_err", utils.escape(plugin_uuid)), show_alert=True)
            return

        plugin_path_to_delete = plugin_to_delete.path
        plugin_name_for_log_and_msg = plugin_to_delete.name # Сохраняем имя для сообщения

        if not os.path.exists(plugin_path_to_delete):
            # pl_file_not_found_err уже локализован
            bot.answer_callback_query(c.id, _("pl_file_not_found_err", utils.escape(plugin_path_to_delete)),
                                      show_alert=True)
            # Удаляем плагин из словаря, даже если файла нет, чтобы не было "фантомов"
            if plugin_uuid in cortex_instance.plugins:
                cortex_instance.plugins.pop(plugin_uuid)
            c.data = f"{CBT.PLUGINS_LIST}:{offset}"
            open_plugins_list(c) # Обновляем список
            return

        if plugin_to_delete.delete_handler:
            try:
                plugin_to_delete.delete_handler(cortex_instance, c) # Вызываем обработчик удаления, если он есть
            except Exception as e:
                # log_pl_delete_handler_err уже локализован
                logger.error(_("log_pl_delete_handler_err", plugin_name_for_log_and_msg))
                logger.debug(f"Ошибка в delete_handler плагина {plugin_name_for_log_and_msg}: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                # Можно добавить уведомление пользователю об ошибке в хендлере
                # Добавим ключ pl_delete_handler_failed = "Ошибка при выполнении обработчика удаления плагина {plugin_name}. Плагин удален, но могут остаться его данные."
                bot.answer_callback_query(c.id, _("pl_delete_handler_failed", plugin_name=utils.escape(plugin_name_for_log_and_msg), language=localizer.current_language), show_alert=True)
        
        try:
            os.remove(plugin_path_to_delete)
            logger.info(_("log_pl_deleted", c.from_user.username, c.from_user.id, plugin_name_for_log_and_msg))
            if plugin_uuid in cortex_instance.plugins: # Удаляем из активных плагинов
                cortex_instance.plugins.pop(plugin_uuid)
            
            # Обновляем список плагинов
            # Корректируем offset
            all_plugins_after_delete = list(sorted(cortex_instance.plugins.keys(), key=lambda x_uuid: cortex_instance.plugins[x_uuid].name.lower()))
            new_offset = max(0, offset - MENU_CFG.PLUGINS_BTNS_AMOUNT if offset >= MENU_CFG.PLUGINS_BTNS_AMOUNT and len(all_plugins_after_delete) < offset + MENU_CFG.PLUGINS_BTNS_AMOUNT else offset)
            new_offset = 0 if len(all_plugins_after_delete) <= MENU_CFG.PLUGINS_BTNS_AMOUNT else new_offset

            c.data = f"{CBT.PLUGINS_LIST}:{new_offset}"
            open_plugins_list(c) # Обновляем сообщение со списком
             # Добавим ключ pl_deleted_successfully = "Плагин '{plugin_name}' успешно удален."
            bot.answer_callback_query(c.id, _("pl_deleted_successfully", plugin_name=utils.escape(plugin_name_for_log_and_msg), language=localizer.current_language), show_alert=True)
        except Exception as e:
            logger.error(f"Не удалось удалить файл плагина {plugin_path_to_delete}: {e}")
            # Добавим ключ pl_file_delete_error = "Не удалось удалить файл плагина '{plugin_path}'. Проверьте права доступа."
            bot.answer_callback_query(c.id, _("pl_file_delete_error", plugin_path=utils.escape(plugin_path_to_delete), language=localizer.current_language), show_alert=True)


    def act_upload_plugin(obj: CallbackQuery | Message):
        # pl_new уже локализован
        text_prompt = _("pl_new") 
        
        if isinstance(obj, CallbackQuery):
            offset = int(obj.data.split(":")[1])
            result = bot.send_message(obj.message.chat.id, text_prompt, reply_markup=CLEAR_STATE_BTN())
            tg.set_state(obj.message.chat.id, result.id, obj.from_user.id, CBT.UPLOAD_PLUGIN, {"offset": offset})
            bot.answer_callback_query(obj.id)
        elif isinstance(obj, Message): # Если это команда /upload_plugin
            result = bot.send_message(obj.chat.id, text_prompt, reply_markup=CLEAR_STATE_BTN())
            # По умолчанию offset 0, если вызвано командой
            tg.set_state(obj.chat.id, result.id, obj.from_user.id, CBT.UPLOAD_PLUGIN, {"offset": 0}) 

    # Регистрация хэндлеров (без изменений)
    tg.cbq_handler(open_plugins_list, lambda c: c.data.startswith(f"{CBT.PLUGINS_LIST}:"))
    tg.cbq_handler(open_edit_plugin_cp, lambda c: c.data.startswith(f"{CBT.EDIT_PLUGIN}:"))
    tg.cbq_handler(open_plugin_commands, lambda c: c.data.startswith(f"{CBT.PLUGIN_COMMANDS}:"))
    tg.cbq_handler(toggle_plugin, lambda c: c.data.startswith(f"{CBT.TOGGLE_PLUGIN}:"))

    tg.cbq_handler(ask_delete_plugin, lambda c: c.data.startswith(f"{CBT.DELETE_PLUGIN}:"))
    tg.cbq_handler(cancel_delete_plugin, lambda c: c.data.startswith(f"{CBT.CANCEL_DELETE_PLUGIN}:"))
    tg.cbq_handler(delete_plugin, lambda c: c.data.startswith(f"{CBT.CONFIRM_DELETE_PLUGIN}:"))

    tg.cbq_handler(act_upload_plugin, lambda c: c.data.startswith(f"{CBT.UPLOAD_PLUGIN}:"))
    tg.msg_handler(act_upload_plugin, commands=["upload_plugin"]) # Добавляем обработку команды


BIND_TO_PRE_INIT = [init_plugins_cp]