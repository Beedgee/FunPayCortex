"""
В данном модуле реализован загрузчик файлов из телеграм чата.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from cardinal import Cortex # Renamed FPCortex to Cortex
    from tg_bot.bot import TGBot

from Utils import config_loader as cfg_loader, exceptions as excs, cardinal_tools # Renamed from Utils
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup as K # Добавил K
from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot import types
import logging
import os
from locales.localizer import Localizer # Импорт Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer() # Инициализация
_ = localizer.translate # Алиас для перевода

# Добавим ключи для локализации сообщений об ошибках
# file_err_not_detected = "❌ Файл не обнаружен."
# file_err_must_be_text = "❌ Файл должен быть текстовым (например, .txt, .cfg, .py, .json)."
# file_err_wrong_format = "❌ Неправильный формат файла: <b><u>.{actual_ext}</u></b> (ожидался <b><u>.{expected_ext}</u></b>)."
# file_err_too_large = "❌ Размер файла не должен превышать 20МБ."
# file_info_downloading = "⏬ Загружаю файл..."
# file_err_download_failed = "❌ Произошла ошибка при загрузке файла на сервер."
# file_info_checking_validity = "🔁 Проверяю валидность файла..."
# file_err_processing_generic = "❌ Произошла ошибка при обработке файла: <code>{error_message}</code>"
# file_err_utf8_decode = "Произошла ошибка при расшифровке UTF-8. Убедитесь, что кодировка файла = UTF-8, а формат конца строк = LF."
# file_info_main_cfg_loaded = "✅ Основной конфиг успешно загружен.\n⚠️ Необходимо перезапустить бота, чтобы применить изменения.\nЛюбое изменение основного конфига через переключатели в ПУ отменит эти изменения."
# file_info_ar_cfg_applied = "✅ Конфиг автоответчика успешно применен."
# file_info_ad_cfg_applied = "✅ Конфиг автовыдачи успешно применен."
# plugin_uploaded_success = "✅ Плагин <code>{filename}</code> успешно загружен.\n\n⚠️Чтобы плагин активировался, <b><u>перезагрузите FPCortex!</u></b> (/restart)"
# image_upload_unsupported_format = "❌ Поддерживаются только форматы: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>." # Добавлен jpeg
# image_upload_error_generic = "❌ Не удалось выгрузить изображение. Подробнее в файле <code>logs/log.log</code>"
# image_upload_chat_success_info = "Используйте этот ID в текстах автовыдачи/автоответа с переменной <code>$photo</code>\n\nНапример: <code>$photo={image_id}</code>"
# image_upload_offer_success_info = "Используйте этот ID для добавления картинок к лотам."
# image_upload_success_header = "✅ Изображение выгружено на сервер FunPay.\n\n<b>ID:</b> <code>{image_id}</code>\n\n"
# products_file_provide_prompt = "📎 Отправьте мне файл с товарами (.txt):"
# products_file_upload_success = "✅ Файл с товарами <code>{filepath}</code> успешно загружен. Товаров в файле: <code>{count}</code>."
# products_file_count_error = "⚠️ Произошла ошибка при подсчете товаров в загруженном файле."
# main_config_provide_prompt = "⚙️ Отправьте мне основной конфиг (_main.cfg):"
# ar_config_provide_prompt = "🤖 Отправьте мне конфиг автоответчика (auto_response.cfg):"
# ad_config_provide_prompt = "📦 Отправьте мне конфиг автовыдачи (auto_delivery.cfg):"

def check_file(tg: TGBot, msg: types.Message, type_: Literal["py", "cfg", "json", "txt"] | None = None) -> bool:
    bot = tg.bot # Для краткости
    if not msg.document:
        bot.send_message(msg.chat.id, _("file_err_not_detected"))
        return False
    
    file_name = msg.document.file_name
    actual_ext = file_name.split('.')[-1].lower() if '.' in file_name else ""

    allowed_text_exts = ["cfg", "txt", "py", "json", "ini", "log"] # Расширим немного
    if actual_ext not in allowed_text_exts:
        bot.send_message(msg.chat.id, _("file_err_must_be_text"))
        return False
        
    if type_ is not None and actual_ext != type_.lower():
        bot.send_message(msg.chat.id, _("file_err_wrong_format", actual_ext=actual_ext, expected_ext=type_))
        return False
        
    if msg.document.file_size >= 20971520: # 20MB
        bot.send_message(msg.chat.id, _("file_err_too_large"))
        return False
    return True


def download_file(tg: TGBot, msg: types.Message, file_name: str = "temp_file.txt",
                  custom_path: str = "") -> str | None: # Возвращает путь к файлу или None
    bot = tg.bot
    bot.send_message(msg.chat.id, _("file_info_downloading"))
    try:
        file_info = bot.get_file(msg.document.file_id)
        downloaded_file_bytes = bot.download_file(file_info.file_path)
    except Exception as e:
        logger.error(f"Ошибка скачивания файла от Telegram: {e}")
        bot.send_message(msg.chat.id, _("file_err_download_failed"))
        logger.debug("TRACEBACK", exc_info=True)
        return None

    # Формируем путь и создаем директории, если их нет
    target_dir = custom_path if custom_path else os.path.join("storage", "cache")
    os.makedirs(target_dir, exist_ok=True)
    
    # Используем оригинальное имя файла, если оно передано и не "temp_file.txt"
    # или если file_name не указан явно (т.е. используется значение по умолчанию)
    final_file_name = msg.document.file_name if file_name == "temp_file.txt" else file_name
    
    full_path = os.path.join(target_dir, final_file_name)
    
    try:
        with open(full_path, "wb") as new_file:
            new_file.write(downloaded_file_bytes)
        return full_path # Возвращаем полный путь к сохраненному файлу
    except Exception as e:
        logger.error(f"Ошибка сохранения скачанного файла {full_path}: {e}")
        bot.send_message(msg.chat.id, _("file_err_download_failed")) # Можно уточнить ошибку сохранения
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
        
        # download_file теперь использует оригинальное имя файла по умолчанию
        saved_file_path = download_file(tg, m, custom_path="storage/products")
        if not saved_file_path:
            return

        products_count_str = "⚠️"
        try:
            products_count_str = str(cardinal_tools.count_products(saved_file_path))
        except Exception:
            bot.send_message(m.chat.id, _("products_file_count_error"))
            logger.debug("TRACEBACK", exc_info=True)
            # Файл все равно загружен, так что можно не удалять его сразу

        # Определение file_number для кнопки редактирования
        # Это может быть сложно, если имя файла не уникально или содержит спецсимволы
        # Проще просто предложить вернуться в меню файлов товаров
        products_dir = "storage/products"
        all_files_in_storage = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []
        try:
            file_index_for_button = all_files_in_storage.index(os.path.basename(saved_file_path))
            offset_for_button = utils.get_offset(file_index_for_button, MENU_CFG.PF_BTNS_AMOUNT)
            edit_button = Button(_("gl_edit"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_index_for_button}:{offset_for_button}")
        except ValueError: # Если файл не найден в списке (маловероятно)
            edit_button = Button(_("ad_edit_goods_file"), callback_data=f"{CBT.PRODUCTS_FILES_LIST}:0") # Возврат к списку файлов

        keyboard_reply = K().add(edit_button)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил файл с товарами $YELLOW{saved_file_path}$RESET.")
        bot.send_message(m.chat.id,
                         _("products_file_upload_success", filepath=utils.escape(saved_file_path), count=products_count_str),
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
        
        # Сохраняем с временным именем для проверки
        temp_config_path = download_file(tg, m, file_name="temp_main.cfg") 
        if not temp_config_path:
            return

        bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_config = cfg_loader.load_main_config(temp_config_path)
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            if os.path.exists(temp_config_path): os.remove(temp_config_path) # Удаляем временный файл
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id, _("file_err_utf8_decode"))
            if os.path.exists(temp_config_path): os.remove(temp_config_path)
            return
        except Exception as e: # Общий обработчик на непредвиденные ошибки парсинга
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_config_path): os.remove(temp_config_path)
            return

        # Если проверка прошла, заменяем основной конфиг
        cortex_instance.save_config(new_config, "configs/_main.cfg") # Этот метод должен корректно сохранять
        if os.path.exists(temp_config_path): os.remove(temp_config_path) # Удаляем временный файл

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

        bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_ar_config = cfg_loader.load_auto_response_config(temp_ar_cfg_path)
            raw_new_ar_config = cfg_loader.load_raw_auto_response_config(temp_ar_cfg_path)
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id, _("file_err_utf8_decode"))
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return
        except Exception as e:
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_ar_cfg_path): os.remove(temp_ar_cfg_path)
            return

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

        bot.send_message(m.chat.id, _("file_info_checking_validity"))
        try:
            new_ad_config = cfg_loader.load_auto_delivery_config(temp_ad_cfg_path)
        except excs.ConfigParseError as e:
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return
        except UnicodeDecodeError:
            bot.send_message(m.chat.id, _("file_err_utf8_decode"))
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return
        except Exception as e:
            bot.send_message(m.chat.id, _("file_err_processing_generic", error_message=utils.escape(str(e))))
            logger.debug("TRACEBACK", exc_info=True)
            if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)
            return

        cortex_instance.AD_CFG = new_ad_config
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
        if os.path.exists(temp_ad_cfg_path): os.remove(temp_ad_cfg_path)

        logger.info(f"Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил и применил конфиг автовыдачи.")
        bot.send_message(m.chat.id, _("file_info_ad_cfg_applied"))

    def upload_plugin_handler(m: types.Message): # Переименовал, чтобы не конфликтовать с CBT.UPLOAD_PLUGIN
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        offset = state_data["data"].get("offset", 0) if state_data and state_data.get("data") else 0
        tg.clear_state(m.chat.id, m.from_user.id, True)
        
        if not check_file(tg, m, type_="py"):
            return
        
        # Используем оригинальное имя файла плагина
        saved_plugin_path = download_file(tg, m, custom_path="plugins")
        if not saved_plugin_path:
            return

        original_plugin_filename = os.path.basename(saved_plugin_path)

        logger.info(f"[IMPORTANT] Пользователь $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET "
                    f"загрузил плагин $YELLOW{saved_plugin_path}$RESET.")

        # gl_back уже локализован
        keyboard_reply = K().add(Button(_("gl_back"), callback_data=f"{CBT.PLUGINS_LIST}:{offset}"))
        # plugin_uploaded_success уже локализован
        bot.send_message(m.chat.id,
                         _("plugin_uploaded_success", filename=utils.escape(original_plugin_filename)),
                         reply_markup=keyboard_reply)

    def send_funpay_image_handler(m: types.Message): # Переименовал
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        if not state_data or not state_data.get("data"): # Проверка на None
            # Если состояния нет, возможно, оно было очищено. Просто выходим.
            logger.warning(f"Попытка отправить изображение в FunPay без активного состояния для пользователя {m.from_user.id}")
            return

        node_id = state_data["data"].get("node_id")
        username = state_data["data"].get("username")
        tg.clear_state(m.chat.id, m.from_user.id, True)

        if node_id is None or username is None: # Дополнительная проверка
            logger.error(f"Отсутствуют node_id или username в состоянии для отправки изображения FunPay (user: {m.from_user.id})")
            bot.reply_to(m, _("gl_error_try_again"))
            return

        if not m.photo:
            # image_upload_unsupported_format уже локализован
            bot.send_message(m.chat.id, _("image_upload_unsupported_format"))
            return
            
        photo_obj = m.photo[-1] # Берем самое большое разрешение
        if photo_obj.file_size >= 20971520: # 20MB
            bot.send_message(m.chat.id, _("file_err_too_large"))
            return

        try:
            file_info = bot.get_file(photo_obj.file_id)
            downloaded_image_bytes = bot.download_file(file_info.file_path)
            
            # Загружаем изображение на FunPay
            image_id_on_fp = cortex_instance.account.upload_image(downloaded_image_bytes, type_="chat")
            # Отправляем сообщение с изображением
            send_result = cortex_instance.account.send_message(node_id, None, username, image_id_on_fp)
            
            reply_keyboard_after_send = keyboards.reply(node_id, username, again=True, extend=True) # Клавиатура уже локализована
            if not send_result:
                # msg_sending_error уже локализован
                bot.reply_to(m, _("msg_sending_error", node_id, username), reply_markup=reply_keyboard_after_send)
                return
            # msg_sent уже локализован
            bot.reply_to(m, _("msg_sent", node_id, username), reply_markup=reply_keyboard_after_send)
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения в чат FunPay {node_id}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            # image_upload_error_generic уже локализован
            bot.reply_to(m, _("image_upload_error_generic"),
                         reply_markup=keyboards.reply(node_id, username, again=True, extend=True)) # Клавиатура на случай ошибки
            return

    def upload_image_generic_handler(m: types.Message, image_type: Literal["chat", "offer"]): # Общая функция для /upload_chat_img и /upload_offer_img
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not m.photo:
            bot.send_message(m.chat.id, _("image_upload_unsupported_format"))
            return
            
        photo_obj = m.photo[-1]
        if photo_obj.file_size >= 20971520: # 20MB
            bot.send_message(m.chat.id, _("file_err_too_large"))
            return

        try:
            file_info = bot.get_file(photo_obj.file_id)
            downloaded_image_bytes = bot.download_file(file_info.file_path)
            image_id_on_fp = cortex_instance.account.upload_image(downloaded_image_bytes, type_=image_type)
        except Exception as e:
            logger.error(f"Ошибка при выгрузке изображения типа '{image_type}': {e}")
            logger.debug("TRACEBACK", exc_info=True)
            bot.reply_to(m, _("image_upload_error_generic"))
            return
        
        # Формируем информационное сообщение
        # image_upload_success_header уже локализован
        success_message_header = _("image_upload_success_header", image_id=image_id_on_fp)
        
        additional_info_key = "image_upload_chat_success_info" if image_type == "chat" else "image_upload_offer_success_info"
        additional_info_text = _(additional_info_key, image_id=image_id_on_fp) # Передаем image_id для возможной подстановки
        
        bot.reply_to(m, f"{success_message_header}{additional_info_text}")

    def upload_chat_image_handler(m: types.Message):
        upload_image_generic_handler(m, type_="chat")

    def upload_offer_image_handler(m: types.Message):
        upload_image_generic_handler(m, type_="offer")

    # Регистрация обработчиков
    tg.cbq_handler(act_upload_products_file, lambda c: c.data == CBT.UPLOAD_PRODUCTS_FILE)
    tg.cbq_handler(act_upload_auto_response_config, lambda c: c.data == "upload_auto_response_config")
    tg.cbq_handler(act_upload_auto_delivery_config, lambda c: c.data == "upload_auto_delivery_config")
    tg.cbq_handler(act_upload_main_config, lambda c: c.data == "upload_main_config")

    # Используем новые имена для хэндлеров файлов
    tg.file_handler(CBT.UPLOAD_PRODUCTS_FILE, upload_products_file)
    tg.file_handler("upload_auto_response_config", upload_auto_response_config)
    tg.file_handler("upload_auto_delivery_config", upload_auto_delivery_config)
    tg.file_handler("upload_main_config", upload_main_config)
    tg.file_handler(CBT.UPLOAD_PLUGIN, upload_plugin_handler) # Обновлено имя хэндлера
    tg.file_handler(CBT.SEND_FP_MESSAGE, send_funpay_image_handler) # Обновлено имя хэндлера (для изображений в чат FunPay)
    tg.file_handler(CBT.UPLOAD_CHAT_IMAGE, upload_chat_image_handler) # Обновлено имя хэндлера
    tg.file_handler(CBT.UPLOAD_OFFER_IMAGE, upload_offer_image_handler) # Обновлено имя хэндлера


BIND_TO_PRE_INIT = [init_uploader]