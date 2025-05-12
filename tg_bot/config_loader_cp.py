"""
В данном модуле описаны функции для ПУ загрузки / выгрузки конфиг-файлов.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cardinal import Cortex # Renamed FPCortex to Cortex

from tg_bot import CBT, static_keyboards
from telebot import types
import logging
import os

from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_config_loader_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def open_config_loader(c: types.CallbackQuery):
        # desc_cfg уже локализован
        text_to_send = _("desc_cfg")
        reply_markup_kb = static_keyboards.CONFIGS_UPLOADER() # Клавиатура уже использует локализацию

        if c.message.text is None or c.message.content_type != 'text': # Если это не текстовое сообщение (например, фото с клавиатурой)
            bot.delete_message(c.message.chat.id, c.message.id) # Удаляем старое нетекстовое сообщение
            bot.send_message(c.message.chat.id, text_to_send, reply_markup=reply_markup_kb)
        else:
            bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id,
                                  reply_markup=reply_markup_kb)
        bot.answer_callback_query(c.id)


    def send_config(c: types.CallbackQuery):
        config_type_key = c.data.split(":")[1]
        
        # Словарь для маппинга ключей на пути и описания
        config_details = {
            "main": ("configs/_main.cfg", _("cfg_main")),
            "autoResponse": ("configs/auto_response.cfg", _("cfg_ar")),
            "autoDelivery": ("configs/auto_delivery.cfg", _("cfg_ad"))
        }

        if config_type_key not in config_details:
            bot.answer_callback_query(c.id, _("gl_error_try_again") + " (unknown config type)", show_alert=True) # Добавим пояснение для разработчика
            return

        path, caption_text = config_details[config_type_key]
        
        # cfg_main, cfg_ar, cfg_ad уже локализованы и используются в caption_text
        # gl_back уже локализован
        back_button_kb = types.InlineKeyboardMarkup() \
            .add(types.InlineKeyboardButton(_("gl_back"), callback_data=CBT.CONFIG_LOADER))

        if not os.path.exists(path):
            # cfg_not_found_err уже локализован
            bot.answer_callback_query(c.id, _("cfg_not_found_err", path), show_alert=True)
            return

        try:
            with open(path, "r", encoding="utf-8") as f_read:
                data_content = f_read.read().strip()
                if not data_content:
                    # cfg_empty_err уже локализован
                    bot.answer_callback_query(c.id, _("cfg_empty_err", path), show_alert=True)
                    return
            # Открываем в бинарном режиме для отправки
            with open(path, "rb") as f_send:
                bot.send_document(c.message.chat.id, f_send, caption=caption_text, reply_markup=back_button_kb)
            
            # log_cfg_downloaded уже локализован
            logger.info(_("log_cfg_downloaded", c.from_user.username, c.from_user.id, path))
            bot.answer_callback_query(c.id)
        except Exception as e:
            logger.error(f"Ошибка при отправке конфига {path}: {e}")
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)


    tg.cbq_handler(open_config_loader, lambda c: c.data == CBT.CONFIG_LOADER)
    tg.cbq_handler(send_config, lambda c: c.data.startswith(f"{CBT.DOWNLOAD_CFG}:"))


BIND_TO_PRE_INIT = [init_config_loader_cp]