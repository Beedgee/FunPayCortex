# START OF FILE FunPayCortex/tg_bot/file_uploader.py

"""
В данном модуле реализован загрузчик файлов из телеграм чата.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from cortex import Cortex
    from tg_bot.bot import TGBot

from Utils import config_loader as cfg_loader, exceptions as excs, cortex_tools
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup as K
from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot import types, apihelper # Добавил apihelper для проверки кодов ошибок
import logging
import os
from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def check_file(tg: TGBot, msg: types.Message, type_: Literal["py", "cfg", "json", "txt"] | None = None) -> bool:
    bot = tg.bot
    if not msg.document:
        bot.send_message(msg.chat.id, _("file_err_not_detected"))
        return False

    file_name = msg.document.file_name
    actual_ext = file_name.split('.')[-1].lower() if '.' in file_name else ""

    allowed_text_exts = ["cfg", "txt", "py", "json", "ini", "log"]
    if type_ and type_ not in allowed_text_exts : # Если type_ не текстовый, то он должен быть явно разрешен
        if actual_ext != type_.lower():
            bot.send_message(msg.chat.id, _("file_err_wrong_format", actual_ext=actual_ext, expected_ext=type_))
            return False
    elif actual_ext not in allowed_text_exts : # Если type_ не указан (или текстовый) и расширение не в списке
        bot.send_message(msg.chat.id, _("file_err_must_be_text"))
        return False
    elif type_ and actual_ext != type_.lower(): # Если type_ текстовый, но расширение не совпадает
        bot.send_message(msg.chat.id, _("file_err_wrong_format", actual_ext=actual_ext, expected_ext=type_))
        return False


    if msg.document.file_size >= 20971520: # 20MB
        bot.send_message(msg.chat.id, _("file_err_too_large"))
        return False
    return True


def download_file(tg: TGBot, msg: types.Message, file_name: str = "temp_file.txt",
                  custom_path: str = "") -> str | None:
    bot = tg.bot
    progress_msg = bot.send_message(msg.chat.id, _("file_info_downloading"))
    try:
        file_info = bot.get_file(msg.document.file_id)
        downloaded_file_bytes = bot.download_file(file_info.file_path)
    except apihelper.ApiTelegramException as e: # Ловим специфичную ошибку Telegram API
        logger.error(f"Ошибка Telegram API при скачивании файла: {e}")
        bot.edit_message_text(_("file_err_download_failed") + f" (API Error: {e.error_code})", progress_msg.chat.id, progress_msg.id)
        return None
    except Exception as e:
        logger.error(f"Ошибка скачивания файла от Telegram: {e}")
        bot.edit_message_text(_("file_err_download_failed"), progress_msg.chat.id, progress_msg.id)
        logger.debug("TRACEBACK", exc_info=True)
        return None

    target_dir = custom_path if custom_path else os.path.join("storage", "cache")
    os.makedirs(target_dir, exist_ok=True)

    final_file_name = msg.document.file_name if file_name == "temp_file.txt" else file_name
    full_path = os.path.join(target_dir, final_file_name)

    try:
        with open(full_path, "wb") as new_file:
            new_file.write(downloaded_file_bytes)
        bot.delete_message(progress_msg.chat.id, progress_msg.id) # Удаляем сообщение "Загружаю..."
        return full_path
    except IOError as e: # Ловим ошибки ввода-вывода при сохранении
        logger.error(f"Ошибка сохранения скачанного файла {full_path}: {e}")
        bot.edit_message_text(_("file_err_download_failed") + " (Save Error)", progress_msg.chat.id, progress_msg.id)
        return None
    except Exception as e: # Общая ошибка на всякий случай
        logger.error(f"Неожиданная ошибка при сохранении скачанного файла {full_path}: {e}")
        bot.edit_message_text(_("file_err_download_failed") + " (Unexpected Save Error)", progress_msg.chat.id, progress_msg.id)
        logger.debug("TRACEBACK", exc_info=True)
        return None


def init_uploader(cortex_instance: Cortex):
    tg = cortex_instance.telegram
    bot = tg.bot

    def act_upload_products_file(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("products_file_provide_prompt"),
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.UPLOAD_PRODUCTS_FILE)
        bot.answer_callback_query(c.id)

    def upload_products_file(m: types.Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="txt"):
            return

        saved_file_path = download_file(tg, m, custom_path="storage/products")
        if not saved_file_path:
            return

        products_count_str = "⚠️"
        try:
            products_count_str = str(cortex_tools.count_products(saved_file_path))
        except Exception as e: # Более общее исключение, если count_products выдаст ошибку
            bot.send_message(m.chat.id, _("products_file_count_error") + f"\nError: {str(e)[:100]}")
            logger.error(f"Ошибка подсчета товаров в файле {saved_file_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            # Файл все равно загружен, так что можно не удалять его сразу

        products_dir = "storage/products"
        all_files_in_storage = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []
        try:
            file_index_for_button = all_files_in_storage.index(os.path.basename(saved_file_path))
            offset_for_button = utils.get_offset(file_index_for_button, MENU_CFG.PF_BTNS_AMOUNT)
            edit_button = Button(_("gl_edit"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_index_for_button}:{offset_for_button}")
        except ValueError:
            edit_button = Button(_("ad_edit_goods_file"), callback_data=f"{CBT.PRODUCTS_FILES_LIST}:0")

        keyboard_reply = K().add(edit_button)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил файл с товарами $YELLOW{saved_file_path}$RESET.")
        bot.send_message(m.chat.id,
                         _("products_file_upload_success", utils.escape(saved_file_path), products_count_str),
                         reply_markup=keyboard_reply)

    def act_upload_main_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("main_config_provide_prompt"),
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_main_config")
        bot.answer_callback_query(c.id)

    def upload_main_config(m: types.Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return

        temp_config_path = download_file(tg, m, file_name="temp_main.cfg")
        if not temp_config_path:
            return

        progress_msg_check = bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_config = cfg_loader.load_main_config(temp_config_path)
        except excs.ConfigParseError as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_config_path): os.remove(temp_config_path)
            return
        except UnicodeDecodeError:
            bot.edit_message_text(_("file_err_utf8_decode"), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_config_path): os.remove(temp_config_path)
            return
        except Exception as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            logger.error(f"Непредвиденная ошибка при парсинге основного конфига {temp_config_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_config_path): os.remove(temp_config_path)
            return
        bot.delete_message(progress_msg_check.chat.id, progress_msg_check.id)

        cortex_instance.save_config(new_config, "configs/_main.cfg")
        if os.path.exists(temp_config_path): os.remove(temp_config_path)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил в бота основной конфиг.")
        bot.send_message(m.chat.id, _("file_info_main_cfg_loaded"))

    def act_upload_auto_response_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("ar_config_provide_prompt"),
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_auto_response_config")
        bot.answer_callback_query(c.id)

    def upload_auto_response_config(m: types.Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return

        temp_ar_cfg_path = download_file(tg, m, file_name="temp_auto_response.cfg")
        if not temp_ar_cfg_path:
            return

        progress_msg_check = bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_ar_config = cfg_loader.load_auto_response_config(temp_ar_cfg_path)
            raw_new_ar_config = cfg_loader.load_raw_auto_response_config(temp_ar_cfg_path)
        except excs.ConfigParseError as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return
        except UnicodeDecodeError:
            bot.edit_message_text(_("file_err_utf8_decode"), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return
        except Exception as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            logger.error(f"Непредвиденная ошибка при парсинге конфига автоответчика {temp_ar_cfg_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return
        bot.delete_message(progress_msg_check.chat.id, progress_msg_check.id)

        cortex_instance.RAW_AR_CFG, cortex_instance.AR_CFG = raw_new_ar_config, new_ar_config
        cortex_instance.save_config(cortex_instance.RAW_AR_CFG, "configs/auto_response.cfg")
        if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил и применил конфиг автоответчика.")
        bot.send_message(m.chat.id, _("file_info_ar_cfg_applied"))

    def act_upload_auto_delivery_config(c: types.CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("ad_config_provide_prompt"),
                                  reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, "upload_auto_delivery_config")
        bot.answer_callback_query(c.id)

    def upload_auto_delivery_config(m: types.Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_file(tg, m, type_="cfg"):
            return

        temp_ad_cfg_path = download_file(tg, m, file_name="temp_auto_delivery.cfg")
        if not temp_ad_cfg_path:
            return

        progress_msg_check = bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_ad_config = cfg_loader.load_auto_delivery_config(temp_ad_cfg_path)
        except excs.ConfigParseError as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return
        except UnicodeDecodeError:
            bot.edit_message_text(_("file_err_utf8_decode"), progress_msg_check.chat.id, progress_msg_check.id)
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return
        except Exception as e:
            bot.edit_message_text(_("file_err_processing_generic", utils.escape(str(e))), progress_msg_check.chat.id, progress_msg_check.id)
            logger.error(f"Непредвиденная ошибка при парсинге конфига автовыдачи {temp_ad_cfg_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return
        bot.delete_message(progress_msg_check.chat.id, progress_msg_check.id)


        cortex_instance.AD_CFG = new_ad_config
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
        if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил и применил конфиг автовыдачи.")
        bot.send_message(m.chat.id, _("file_info_ad_cfg_applied"))

    def upload_plugin_handler(m: types.Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        offset = state_data["data"].get("offset", 0) if state_data and state_data.get("data") else 0
        tg.clear_state(m.chat.id, m.from_user.id, True)

        if not check_file(tg, m, type_="py"):
            return

        saved_plugin_path = download_file(tg, m, custom_path="plugins")
        if not saved_plugin_path:
            return

        original_plugin_filename = os.path.basename(saved_plugin_path)

        logger.info(f"[IMPORTANT] Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил плагин $YELLOW{saved_plugin_path}$RESET.")

        keyboard_reply = K().add(Button(_("gl_back"), callback_data=f"{CBT.PLUGINS_LIST}:{offset}"))
        bot.send_message(m.chat.id,
                         _("plugin_uploaded_success", utils.escape(original_plugin_filename)), # ИСПРАВЛЕНО
                         reply_markup=keyboard_reply)

    def send_funpay_image_handler(m: types.Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        if not state_data or not state_data.get("data"):
            logger.warning(f"Попытка отправить изображение в FunPay без активного состояния для пользователя {m.from_user.id}")
            return

        node_id = state_data["data"].get("node_id")
        username = state_data["data"].get("username")
        tg.clear_state(m.chat.id, m.from_user.id, True)

        if node_id is None or username is None:
            logger.error(f"Отсутствуют node_id или username в состоянии для отправки изображения FunPay (user: {m.from_user.id})")
            bot.reply_to(m, _("gl_error_try_again"))
            return

        if not m.photo:
            bot.send_message(m.chat.id, _("image_upload_unsupported_format"))
            return

        photo_obj = m.photo[-1]
        if photo_obj.file_size >= 20971520: # 20MB
            bot.send_message(m.chat.id, _("file_err_too_large"))
            return

        progress_msg_upload = bot.send_message(m.chat.id, _("file_info_downloading")) # Сначала "Загружаю..."
        try:
            file_info = bot.get_file(photo_obj.file_id)
            downloaded_image_bytes = bot.download_file(file_info.file_path)

            bot.edit_message_text("📤 Загружаю изображение на FunPay...", progress_msg_upload.chat.id, progress_msg_upload.id)
            image_id_on_fp = cortex_instance.account.upload_image(downloaded_image_bytes, type_="chat")

            bot.edit_message_text("✉️ Отправляю сообщение с изображением...", progress_msg_upload.chat.id, progress_msg_upload.id)
            send_result = cortex_instance.account.send_message(node_id, None, username, image_id=image_id_on_fp) # image_id, а не image
            bot.delete_message(progress_msg_upload.chat.id, progress_msg_upload.id) # Удаляем сообщение о прогрессе

            reply_keyboard_after_send = keyboards.reply(node_id, username, again=True, extend=True)
            if not send_result:
                bot.reply_to(m, _("msg_sending_error", node_id, username), reply_markup=reply_keyboard_after_send)
                return
            bot.reply_to(m, _("msg_sent", node_id, username), reply_markup=reply_keyboard_after_send)
        except Exception as e:
            if 'progress_msg_upload' in locals() and progress_msg_upload: # Проверяем, было ли создано сообщение
                 bot.delete_message(progress_msg_upload.chat.id, progress_msg_upload.id)
            logger.error(f"Ошибка при отправке изображения в чат FunPay {node_id}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            bot.reply_to(m, _("image_upload_error_generic"),
                         reply_markup=keyboards.reply(node_id, username, again=True, extend=True))
            return

    def upload_image_generic_handler(m: types.Message, image_type: Literal["chat", "offer"]):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not m.photo:
            bot.send_message(m.chat.id, _("image_upload_unsupported_format"))
            return

        photo_obj = m.photo[-1]
        if photo_obj.file_size >= 20971520: # 20MB
            bot.send_message(m.chat.id, _("file_err_too_large"))
            return
        
        progress_msg_upload = bot.send_message(m.chat.id, _("file_info_downloading"))
        try:
            file_info = bot.get_file(photo_obj.file_id)
            downloaded_image_bytes = bot.download_file(file_info.file_path)
            
            bot.edit_message_text(f"📤 Загружаю изображение ({image_type}) на FunPay...", progress_msg_upload.chat.id, progress_msg_upload.id)
            image_id_on_fp = cortex_instance.account.upload_image(downloaded_image_bytes, type_=image_type)
            bot.delete_message(progress_msg_upload.chat.id, progress_msg_upload.id)
        except Exception as e:
            if 'progress_msg_upload' in locals() and progress_msg_upload:
                 bot.delete_message(progress_msg_upload.chat.id, progress_msg_upload.id)
            logger.error(f"Ошибка при выгрузке изображения типа '{image_type}': {e}")
            logger.debug("TRACEBACK", exc_info=True)
            bot.reply_to(m, _("image_upload_error_generic"))
            return

        success_message_header = _("image_upload_success_header", image_id_on_fp)
        additional_info_key = "image_upload_chat_success_info" if image_type == "chat" else "image_upload_offer_success_info"
        additional_info_text = _(additional_info_key, image_id_on_fp)

        bot.reply_to(m, f"{success_message_header}{additional_info_text}")

    def upload_chat_image_handler(m: types.Message):
        upload_image_generic_handler(m, type_="chat")

    def upload_offer_image_handler(m: types.Message):
        upload_image_generic_handler(m, type_="offer")

    tg.cbq_handler(act_upload_products_file, lambda c: c.data == CBT.UPLOAD_PRODUCTS_FILE)
    tg.cbq_handler(act_upload_auto_response_config, lambda c: c.data == "upload_auto_response_config")
    tg.cbq_handler(act_upload_auto_delivery_config, lambda c: c.data == "upload_auto_delivery_config")
    tg.cbq_handler(act_upload_main_config, lambda c: c.data == "upload_main_config")

    tg.file_handler(CBT.UPLOAD_PRODUCTS_FILE, upload_products_file)
    tg.file_handler("upload_auto_response_config", upload_auto_response_config)
    tg.file_handler("upload_auto_delivery_config", upload_auto_delivery_config)
    tg.file_handler("upload_main_config", upload_main_config)
    tg.file_handler(CBT.UPLOAD_PLUGIN, upload_plugin_handler)
    tg.file_handler(CBT.SEND_FP_MESSAGE, send_funpay_image_handler)
    tg.file_handler(CBT.UPLOAD_CHAT_IMAGE, upload_chat_image_handler)
    tg.file_handler(CBT.UPLOAD_OFFER_IMAGE, upload_offer_image_handler)


BIND_TO_PRE_INIT = [init_uploader]

# END OF FILE FunPayCortex/tg_bot/file_uploader.py