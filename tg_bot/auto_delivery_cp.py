# START OF FILE FunPayCortex/tg_bot/auto_delivery_cp.py

"""
В данном модуле описаны функции для ПУ конфига автовыдачи.
Модуль реализован в виде плагина.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from tg_bot import utils, keyboards as kb, CBT, MENU_CFG
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery

from Utils import cortex_tools
from locales.localizer import Localizer

import itertools
import random
import string
import logging
import os
import re

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_auto_delivery_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot
    filename_re = re.compile(r"[А-Яа-яЁёA-Za-z0-9_\- .]+")

    def check_ad_lot_exists(index: int, message_obj: Message | CallbackQuery, reply_mode: bool = True) -> bool:
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id

        if index >= len(cortex_instance.AD_CFG.sections()):
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.AD_LOTS_LIST}:0"))
            text_error = _("ad_lot_not_found_err", index)
            if reply_mode and isinstance(message_obj, Message):
                bot.reply_to(message_obj, text_error, reply_markup=update_button)
            else:
                bot.edit_message_text(text_error, chat_id, message_id,
                                      reply_markup=update_button)
            return False
        return True

    def check_products_file_exists(index: int, files_list: list[str],
                                   message_obj: Message | CallbackQuery, reply_mode: bool = True) -> bool:
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id
        
        if index >= len(files_list):
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.PRODUCTS_FILES_LIST}:0"))
            text_error = _("gf_not_found_err", index)
            if reply_mode and isinstance(message_obj, Message):
                bot.reply_to(message_obj, text_error, reply_markup=update_button)
            else:
                bot.edit_message_text(text_error, chat_id, message_id,
                                      reply_markup=update_button)
            return False
        return True

    # Основное меню настроек автовыдачи.
    def open_ad_lots_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_ad_list"), c.message.chat.id, c.message.id,
                              reply_markup=kb.lots_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    def open_fp_lots_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        last_update_time = cortex_instance.last_tg_profile_update.strftime("%d.%m.%Y %H:%M:%S") if cortex_instance.last_tg_profile_update else _("never_updated")
        bot.edit_message_text(_("desc_ad_fp_lot_list", last_update_time),
                              c.message.chat.id, c.message.id, reply_markup=kb.funpay_lots_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    def act_add_lot_manually(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        result = bot.send_message(c.message.chat.id, _("copy_lot_name"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.ADD_AD_TO_LOT_MANUALLY, data={"offset": offset})
        bot.answer_callback_query(c.id)

    def add_lot_manually(m: Message):
        fp_lots_offset = tg.get_state(m.chat.id, m.from_user.id)["data"]["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        lot_title = m.text.strip()

        if lot_title in cortex_instance.AD_CFG.sections():
            error_keyboard = K() \
                .row(B(_("gl_back"), callback_data=f"{CBT.FP_LOTS_LIST}:{fp_lots_offset}"),
                     B(_("ad_add_another_ad"), callback_data=f"{CBT.ADD_AD_TO_LOT_MANUALLY}:{fp_lots_offset}"))
            bot.reply_to(m, _("ad_lot_already_exists", utils.escape(lot_title)), reply_markup=error_keyboard)
            return

        cortex_instance.AD_CFG.add_section(lot_title)
        default_response_text = _("ad_default_response_text_new_lot")
        cortex_instance.AD_CFG.set(lot_title, "response", default_response_text)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
        logger.info(_("log_ad_linked", m.from_user.username, m.from_user.id, lot_title))

        lot_index = len(cortex_instance.AD_CFG.sections()) - 1
        ad_lot_offset = utils.get_offset(lot_index, MENU_CFG.AD_BTNS_AMOUNT)
        keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.FP_LOTS_LIST}:{fp_lots_offset}"),
                 B(_("ad_add_more_ad"), callback_data=f"{CBT.ADD_AD_TO_LOT_MANUALLY}:{fp_lots_offset}"),
                 B(_("gl_configure"), callback_data=f"{CBT.EDIT_AD_LOT}:{lot_index}:{ad_lot_offset}"))
        bot.send_message(m.chat.id, _("ad_lot_linked", utils.escape(lot_title)), reply_markup=keyboard)

    def open_gf_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        bot.edit_message_text(_("desc_gf"), c.message.chat.id, c.message.id,
                              reply_markup=kb.products_files_list(offset))
        bot.answer_callback_query(c.id)

    def act_create_gf(c: CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("act_create_gf"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.CREATE_PRODUCTS_FILE)
        bot.answer_callback_query(c.id)

    def create_gf(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        file_name_input = m.text.strip()

        error_keyboard = K().row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:ad"),
                                 B(_("gf_create_another"), callback_data=CBT.CREATE_PRODUCTS_FILE))

        if not filename_re.fullmatch(file_name_input):
            bot.reply_to(m, _("gf_name_invalid"), reply_markup=error_keyboard)
            return
        
        actual_file_name = file_name_input if file_name_input.lower().endswith(".txt") else file_name_input + ".txt"
        
        products_dir_path = "storage/products"
        if not os.path.exists(products_dir_path):
            os.makedirs(products_dir_path)
            
        full_path = os.path.join(products_dir_path, actual_file_name)

        if os.path.exists(full_path):
            all_files = sorted([f for f in os.listdir(products_dir_path) if f.endswith(".txt")])
            file_index = all_files.index(actual_file_name) if actual_file_name in all_files else -1
            offset_for_kb = utils.get_offset(file_index, MENU_CFG.PF_BTNS_AMOUNT) if file_index != -1 else 0
            keyboard = K() \
                .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:ad"),
                     B(_("gf_create_another"), callback_data=CBT.CREATE_PRODUCTS_FILE),
                     B(_("gl_configure"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_index}:{offset_for_kb}" if file_index != -1 else CBT.EMPTY))
            bot.reply_to(m, _("gf_already_exists_err", utils.escape(actual_file_name)), reply_markup=keyboard)
            return

        try:
            with open(full_path, "w", encoding="utf-8"):
                pass
        except Exception as e:
            logger.error(f"Ошибка создания файла {full_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            bot.reply_to(m, _("gf_creation_err", utils.escape(actual_file_name)), reply_markup=error_keyboard)
            return

        all_files_after_creation = sorted([f for f in os.listdir(products_dir_path) if f.endswith(".txt")])
        try:
            new_file_index = all_files_after_creation.index(actual_file_name)
        except ValueError:
            logger.error(f"Созданный файл {actual_file_name} не найден в списке {products_dir_path}")
            bot.reply_to(m, _("gf_creation_err", utils.escape(actual_file_name)) + " " + _("gl_try_again"), reply_markup=error_keyboard)
            return
            
        offset_for_kb_after_creation = utils.get_offset(new_file_index, MENU_CFG.PF_BTNS_AMOUNT)
        keyboard_success = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:ad"),
                 B(_("gf_create_more"), callback_data=CBT.CREATE_PRODUCTS_FILE),
                 B(_("gl_configure"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{new_file_index}:{offset_for_kb_after_creation}"))
        logger.info(_("log_gf_created", m.from_user.username, m.from_user.id, actual_file_name))
        bot.send_message(m.chat.id, _("gf_created", utils.escape(actual_file_name)), reply_markup=keyboard_success)

    # Меню настройки лотов.
    def open_edit_lot_cp(c: CallbackQuery):
        split_data = c.data.split(":")
        lot_index, offset = int(split_data[1]), int(split_data[2])
        if not check_ad_lot_exists(lot_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        lot_name = cortex_instance.AD_CFG.sections()[lot_index]
        lot_obj = cortex_instance.AD_CFG[lot_name]
        bot.edit_message_text(utils.generate_lot_info_text(lot_obj), c.message.chat.id, c.message.id,
                              reply_markup=kb.edit_lot(cortex_instance, lot_index, offset))
        bot.answer_callback_query(c.id)

    def act_edit_delivery_text(c: CallbackQuery):
        split_data = c.data.split(":")
        lot_index, offset = int(split_data[1]), int(split_data[2])
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_product", "v_order_id", "v_order_link", "v_order_title", "v_game", "v_category",
                     "v_category_fullname", "v_photo", "v_sleep"]
        text_to_send = f"{_('v_edit_delivery_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result = bot.send_message(c.message.chat.id, text_to_send, reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.EDIT_LOT_DELIVERY_TEXT,
                     {"lot_index": lot_index, "offset": offset})
        bot.answer_callback_query(c.id)

    def edit_delivery_text(m: Message):
        user_state = tg.get_state(m.chat.id, m.from_user.id)
        lot_index, offset = user_state["data"]["lot_index"], user_state["data"]["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_ad_lot_exists(lot_index, m):
            return

        new_response_text = m.text.strip()
        lot_name = cortex_instance.AD_CFG.sections()[lot_index]
        lot_obj = cortex_instance.AD_CFG[lot_name]
        keyboard_reply = K().row(B(_("gl_back"), callback_data=f"{CBT.EDIT_AD_LOT}:{lot_index}:{offset}"),
                                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_LOT_DELIVERY_TEXT}:{lot_index}:{offset}"))

        if lot_obj.get("productsFileName") is not None and "$product" not in new_response_text:
            bot.reply_to(m, _("ad_product_var_err", utils.escape(lot_name)), reply_markup=keyboard_reply)
            return

        cortex_instance.AD_CFG.set(lot_name, "response", new_response_text)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
        logger.info(_("log_ad_text_changed", m.from_user.username, m.from_user.id, lot_name, new_response_text))
        bot.reply_to(m, _("ad_text_changed", utils.escape(lot_name), utils.escape(new_response_text)), reply_markup=keyboard_reply)

    def act_link_gf(c: CallbackQuery):
        split_data = c.data.split(":")
        lot_index, offset = int(split_data[1]), int(split_data[2])
        result = bot.send_message(c.message.chat.id, _("ad_link_gf"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.BIND_PRODUCTS_FILE,
                     {"lot_index": lot_index, "offset": offset})
        bot.answer_callback_query(c.id)

    def link_gf(m: Message):
        user_state = tg.get_state(m.chat.id, m.from_user.id)
        lot_index, offset = user_state["data"]["lot_index"], user_state["data"]["offset"]
        tg.clear_state(m.chat.id, m.from_user.id, True)
        if not check_ad_lot_exists(lot_index, m):
            return

        lot_name = cortex_instance.AD_CFG.sections()[lot_index]
        lot_obj = cortex_instance.AD_CFG[lot_name]
        file_name_input = m.text.strip()
        
        keyboard_reply = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.EDIT_AD_LOT}:{lot_index}:{offset}"),
                 B(_("ea_link_another_gf"), callback_data=f"{CBT.BIND_PRODUCTS_FILE}:{lot_index}:{offset}"))

        if file_name_input == "-":
            cortex_instance.AD_CFG.remove_option(lot_name, "productsFileName", fallback=None)
            cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
            logger.info(_("log_gf_unlinked", m.from_user.username, m.from_user.id, lot_name))
            bot.reply_to(m, _("ad_gf_unlinked", utils.escape(lot_name)), reply_markup=keyboard_reply)
            return

        if "$product" not in lot_obj.get("response",""):
            bot.reply_to(m, _("ad_product_var_err2"), reply_markup=keyboard_reply)
            return

        if not filename_re.fullmatch(file_name_input):
            bot.reply_to(m, _("gf_name_invalid"), reply_markup=keyboard_reply)
            return

        actual_file_name_to_link = file_name_input if file_name_input.lower().endswith(".txt") else file_name_input + ".txt"
        full_file_path_to_link = os.path.join("storage", "products", actual_file_name_to_link)
        file_existed_before_linking = os.path.exists(full_file_path_to_link)

        if not file_existed_before_linking:
            bot.send_message(m.chat.id, _("ad_creating_gf", utils.escape(actual_file_name_to_link)))
            try:
                if not os.path.exists(os.path.dirname(full_file_path_to_link)):
                     os.makedirs(os.path.dirname(full_file_path_to_link))
                with open(full_file_path_to_link, "w", encoding="utf-8"):
                    pass
            except Exception as e:
                logger.error(f"Ошибка создания файла при привязке: {full_file_path_to_link}, {e}")
                bot.reply_to(m, _("gf_creation_err", utils.escape(actual_file_name_to_link)), reply_markup=keyboard_reply)
                return

        cortex_instance.AD_CFG.set(lot_name, "productsFileName", actual_file_name_to_link)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")

        if file_existed_before_linking:
            logger.info(_("log_gf_linked", m.from_user.username, m.from_user.id, actual_file_name_to_link, lot_name))
            bot.reply_to(m, _("ad_gf_linked", utils.escape(actual_file_name_to_link), utils.escape(lot_name)), reply_markup=keyboard_reply)
        else:
            logger.info(_("log_gf_created_and_linked", m.from_user.username, m.from_user.id, actual_file_name_to_link, lot_name))
            bot.reply_to(m, _("ad_gf_created_and_linked", utils.escape(actual_file_name_to_link), utils.escape(lot_name)), reply_markup=keyboard_reply)

    def switch_lot_setting(c: CallbackQuery):
        split_data = c.data.split(":")
        param_name, lot_index, offset = split_data[1], int(split_data[2]), int(split_data[3])
        if not check_ad_lot_exists(lot_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        lot_name = cortex_instance.AD_CFG.sections()[lot_index]
        lot_obj = cortex_instance.AD_CFG[lot_name]
        current_value = lot_obj.getboolean(param_name, False)
        new_value_str = str(int(not current_value))
        
        cortex_instance.AD_CFG.set(lot_name, param_name, new_value_str)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")
        logger.info(_("log_param_changed", c.from_user.username, c.from_user.id, param_name, lot_name, new_value_str))
        
        bot.edit_message_text(utils.generate_lot_info_text(lot_obj), c.message.chat.id, c.message.id,
                              reply_markup=kb.edit_lot(cortex_instance, lot_index, offset))
        bot.answer_callback_query(c.id)

    def create_lot_delivery_test(c: CallbackQuery):
        split_data = c.data.split(":")
        lot_index, offset = int(split_data[1]), int(split_data[2])

        if not check_ad_lot_exists(lot_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        lot_name = cortex_instance.AD_CFG.sections()[lot_index]
        test_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        cortex_instance.delivery_tests[test_key] = lot_name

        logger.info(_("log_new_ad_key", c.from_user.username, c.from_user.id, lot_name, test_key))
        keyboard_reply = K().row(B(_("gl_back"), callback_data=f"{CBT.EDIT_AD_LOT}:{lot_index}:{offset}"),
                                 B(_("ea_more_test"), callback_data=f"test_auto_delivery:{lot_index}:{offset}"))
        bot.send_message(c.message.chat.id, _("test_ad_key_created", utils.escape(lot_name), test_key),
                         reply_markup=keyboard_reply)
        bot.answer_callback_query(c.id)

    def del_lot(c: CallbackQuery):
        split_data = c.data.split(":")
        lot_index, offset = int(split_data[1]), int(split_data[2])

        if not check_ad_lot_exists(lot_index, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        lot_name_to_delete = cortex_instance.AD_CFG.sections()[lot_index]
        cortex_instance.AD_CFG.remove_section(lot_name_to_delete)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")

        logger.info(_("log_ad_deleted", c.from_user.username, c.from_user.id, lot_name_to_delete))
        bot.edit_message_text(_("desc_ad_list"), c.message.chat.id, c.message.id,
                              reply_markup=kb.lots_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    # Меню добавления лота с FunPay
    def update_funpay_lots_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        new_msg = bot.send_message(c.message.chat.id, _("ad_updating_lots_list"))
        bot.answer_callback_query(c.id)
        
        update_result = cortex_instance.update_lots_and_categories()
        if not update_result:
            bot.edit_message_text(_("ad_lots_list_updating_err"), new_msg.chat.id, new_msg.id)
            return
        bot.delete_message(new_msg.chat.id, new_msg.id)
        c.data = f"{CBT.FP_LOTS_LIST}:{offset}"
        open_fp_lots_list(c)

    def add_ad_to_lot(c: CallbackQuery):
        split_data = c.data.split(":")
        fp_lot_index, fp_lots_offset = int(split_data[1]), int(split_data[2])
        
        all_fp_lots = cortex_instance.tg_profile.get_common_lots()
        if fp_lot_index >= len(all_fp_lots):
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.FP_LOTS_LIST}:0"))
            bot.edit_message_text(_("ad_lot_not_found_err", fp_lot_index),
                                  c.message.chat.id, c.message.id, reply_markup=update_button)
            bot.answer_callback_query(c.id)
            return

        selected_lot_obj = all_fp_lots[fp_lot_index]
        selected_lot_title = selected_lot_obj.title

        if selected_lot_title in cortex_instance.AD_CFG.sections():
            ad_lot_index_in_cfg = cortex_instance.AD_CFG.sections().index(selected_lot_title)
            offset_for_ad_cfg_kb = utils.get_offset(ad_lot_index_in_cfg, MENU_CFG.AD_BTNS_AMOUNT)
            keyboard_info = K() \
                .row(B(_("gl_back"), callback_data=f"{CBT.FP_LOTS_LIST}:{fp_lots_offset}"),
                     B(_("gl_configure"), callback_data=f"{CBT.EDIT_AD_LOT}:{ad_lot_index_in_cfg}:{offset_for_ad_cfg_kb}"))
            bot.send_message(c.message.chat.id, _("ad_already_ad_err", utils.escape(selected_lot_title)), reply_markup=keyboard_info)
            bot.answer_callback_query(c.id)
            return

        cortex_instance.AD_CFG.add_section(selected_lot_title)
        default_response_text = _("ad_default_response_text_new_lot")
        cortex_instance.AD_CFG.set(selected_lot_title, "response", default_response_text)
        cortex_instance.save_config(cortex_instance.AD_CFG, "configs/auto_delivery.cfg")

        new_ad_lot_index = len(cortex_instance.AD_CFG.sections()) - 1
        offset_for_new_ad_lot_kb = utils.get_offset(new_ad_lot_index, MENU_CFG.AD_BTNS_AMOUNT)
        keyboard_success = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.FP_LOTS_LIST}:{fp_lots_offset}"),
                 B(_("gl_configure"), callback_data=f"{CBT.EDIT_AD_LOT}:{new_ad_lot_index}:{offset_for_new_ad_lot_kb}"))

        logger.info(_("log_ad_linked", c.from_user.username, c.from_user.id, selected_lot_title))
        bot.send_message(c.message.chat.id, _("ad_lot_linked", utils.escape(selected_lot_title)), reply_markup=keyboard_success)
        bot.answer_callback_query(c.id)

    # Меню управления файлов с товарами.
    def open_gf_settings(c: CallbackQuery):
        split_data = c.data.split(":")
        file_index, offset = int(split_data[1]), int(split_data[2])
        
        products_dir = "storage/products"
        all_product_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []

        if not check_products_file_exists(file_index, all_product_files, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        selected_file_name = all_product_files[file_index]
        full_selected_file_path = os.path.join(products_dir, selected_file_name)
        
        products_amount_str = "⚠️"
        try:
            products_amount_str = str(cortex_tools.count_products(full_selected_file_path))
        except Exception:
            pass

        nl = "\n"
        linked_lots_list = [lot_name for lot_name in cortex_instance.AD_CFG.sections() 
                            if cortex_instance.AD_CFG[lot_name].get("productsFileName") == selected_file_name]
        
        linked_lots_display = nl.join(f"<code> • {utils.escape(lot)}</code>" for lot in linked_lots_list) if linked_lots_list \
                              else f"<i>({_('no_lots_using_file')})</i>"

        text_to_send = f"""📄 <b><u>{utils.escape(selected_file_name)}</u></b>

🔢 <b><i>{_('gf_amount')}:</i></b>  <code>{products_amount_str}</code>
🔗 <b><i>{_('gf_uses')}:</i></b>
{linked_lots_display}

⏱️ <i>{_('gl_last_update')}:</i>  <code>{datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"""

        bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id,
                              reply_markup=kb.products_file_edit(file_index, offset))
        bot.answer_callback_query(c.id)

    def act_add_products_to_file(c: CallbackQuery):
        split_data = c.data.split(":")
        file_index, el_index, offset, prev_page = int(split_data[1]), int(split_data[2]), int(split_data[3]), int(split_data[4])
        result = bot.send_message(c.message.chat.id, _("gf_send_new_goods"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.ADD_PRODUCTS_TO_FILE,
                     {"file_index": file_index, "element_index": el_index,
                      "offset": offset, "previous_page": prev_page})
        bot.answer_callback_query(c.id)

    def add_products_to_file(m: Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)["data"]
        file_index, el_index, offset, prev_page = (state_data["file_index"], state_data["element_index"],
                                                   state_data["offset"], state_data["previous_page"])
        tg.clear_state(m.chat.id, m.from_user.id, True)

        products_dir = "storage/products"
        all_product_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []
        
        if file_index >= len(all_product_files):
            update_btn_cb = f"{CBT.PRODUCTS_FILES_LIST}:0" if prev_page == 0 else f"{CBT.EDIT_AD_LOT}:{el_index}:{offset}"
            error_keyboard = K().add(B(_("gl_refresh") if prev_page == 0 else _("gl_back"), callback_data=update_btn_cb))
            bot.reply_to(m, _("gf_not_found_err", file_index), reply_markup=error_keyboard)
            return

        selected_file_name = all_product_files[file_index]
        full_selected_file_path = os.path.join(products_dir, selected_file_name)
        
        products_to_add = [prod.strip() for prod in m.text.strip().split("\n") if prod.strip()]

        back_btn_cb = f"{CBT.EDIT_PRODUCTS_FILE}:{file_index}:{offset}" if prev_page == 0 else f"{CBT.EDIT_AD_LOT}:{el_index}:{offset}"
        try_again_btn_cb = f"{CBT.ADD_PRODUCTS_TO_FILE}:{file_index}:{el_index}:{offset}:{prev_page}"
        add_more_btn_cb = try_again_btn_cb

        if not products_to_add:
            bot.reply_to(m, _("gf_no_products_to_add"), 
                         reply_markup=K().row(B(_("gl_back"), callback_data=back_btn_cb), 
                                            B(_("gf_try_add_again"), callback_data=try_again_btn_cb)))
            return

        products_text_to_write = "\n" + "\n".join(products_to_add)

        try:
            with open(full_selected_file_path, "a", encoding="utf-8") as f:
                if os.path.getsize(full_selected_file_path) > 0 and not products_text_to_write.startswith("\n"):
                    f.write("\n")
                elif os.path.getsize(full_selected_file_path) == 0 and products_text_to_write.startswith("\n"):
                    products_text_to_write = products_text_to_write.lstrip("\n")

                f.write(products_text_to_write)
        except Exception as e:
            logger.error(f"Ошибка добавления товаров в {full_selected_file_path}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            keyboard_error = K().row(B(_("gl_back"), callback_data=back_btn_cb), B(_("gf_try_add_again"), callback_data=try_again_btn_cb))
            bot.reply_to(m, _("gf_add_goods_err"), reply_markup=keyboard_error)
            return

        logger.info(_("log_gf_new_goods", m.from_user.username, m.from_user.id, len(products_to_add), selected_file_name))
        keyboard_success = K().row(B(_("gl_back"), callback_data=back_btn_cb), B(_("gf_add_more"), callback_data=add_more_btn_cb))
        bot.reply_to(m, _("gf_new_goods", len(products_to_add), utils.escape(selected_file_name)), reply_markup=keyboard_success)

    def send_products_file(c: CallbackQuery):
        split_data = c.data.split(":")
        file_index, offset = int(split_data[1]), int(split_data[2])
        
        products_dir = "storage/products"
        all_product_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []

        if not check_products_file_exists(file_index, all_product_files, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return

        selected_file_name = all_product_files[file_index]
        full_selected_file_path = os.path.join(products_dir, selected_file_name)

        try:
            with open(full_selected_file_path, "r", encoding="utf-8") as f:
                data_content = f.read().strip()
                if not data_content:
                    bot.answer_callback_query(c.id, _("gf_empty_error", utils.escape(selected_file_name)), show_alert=True)
                    return
                
                with open(full_selected_file_path, "rb") as file_to_send:
                    bot.send_document(c.message.chat.id, file_to_send, caption=f"📄 {utils.escape(selected_file_name)}")
            logger.info(_("log_gf_downloaded", c.from_user.username, c.from_user.id, selected_file_name))
            bot.answer_callback_query(c.id)
        except FileNotFoundError:
             bot.answer_callback_query(c.id, _("gf_not_found_err", file_index), show_alert=True)
        except Exception as e:
            logger.error(f"Ошибка при отправке файла {selected_file_name}: {e}")
            bot.answer_callback_query(c.id, _("gl_error_try_again"), show_alert=True)


    def ask_del_products_file(c: CallbackQuery):
        split_data = c.data.split(":")
        file_index, offset = int(split_data[1]), int(split_data[2])
        
        products_dir = "storage/products"
        all_product_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []

        if not check_products_file_exists(file_index, all_product_files, c, reply_mode=False):
            bot.answer_callback_query(c.id)
            return
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=kb.products_file_edit(file_index, offset, confirmation=True))
        bot.answer_callback_query(c.id)

    def del_products_file(c: CallbackQuery):
        split_data = c.data.split(":")
        file_index_to_delete, offset = int(split_data[1]), int(split_data[2])
        
        products_dir = "storage/products"
        all_product_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []

        if file_index_to_delete >= len(all_product_files):
            bot.answer_callback_query(c.id, _("gf_not_found_err", file_index_to_delete) + " " + _("gl_refresh_and_try_again"), show_alert=True)
            c.data = f"{CBT.PRODUCTS_FILES_LIST}:{offset}"
            open_gf_list(c)
            return

        file_name_to_delete = all_product_files[file_index_to_delete]
        full_path_to_delete = os.path.join(products_dir, file_name_to_delete)

        linked_lots = [lot_name for lot_name in cortex_instance.AD_CFG.sections() 
                       if cortex_instance.AD_CFG[lot_name].get("productsFileName") == file_name_to_delete]
        if linked_lots:
            keyboard_error = K().add(B(_("gl_back"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_index_to_delete}:{offset}"))
            bot.edit_message_text(_("gf_linked_err", utils.escape(file_name_to_delete)),
                                  c.message.chat.id, c.message.id, reply_markup=keyboard_error)
            bot.answer_callback_query(c.id)
            return

        try:
            os.remove(full_path_to_delete)
            logger.info(_("log_gf_deleted", c.from_user.username, c.from_user.id, file_name_to_delete))
            
            new_offset = max(0, offset - MENU_CFG.PF_BTNS_AMOUNT if offset >= MENU_CFG.PF_BTNS_AMOUNT and len(all_product_files)-1 < offset + MENU_CFG.PF_BTNS_AMOUNT else offset)
            new_offset = 0 if len(all_product_files) -1 <= MENU_CFG.PF_BTNS_AMOUNT else new_offset

            c.data = f"{CBT.PRODUCTS_FILES_LIST}:{new_offset}"
            open_gf_list(c)
            bot.answer_callback_query(c.id, _("gf_deleted_successfully", file_name=utils.escape(file_name_to_delete)), show_alert=True)
        except FileNotFoundError:
            logger.warning(f"Попытка удалить уже удаленный файл: {full_path_to_delete}")
            c.data = f"{CBT.PRODUCTS_FILES_LIST}:{offset}"
            open_gf_list(c)
            bot.answer_callback_query(c.id, _("gf_already_deleted", file_name=utils.escape(file_name_to_delete)), show_alert=True)
        except Exception as e:
            logger.error(f"Ошибка удаления файла {full_path_to_delete}: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            keyboard_error_del = K().add(B(_("gl_back"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_index_to_delete}:{offset}"))
            bot.edit_message_text(_("gf_deleting_err", utils.escape(file_name_to_delete)),
                                  c.message.chat.id, c.message.id, reply_markup=keyboard_error_del)
            bot.answer_callback_query(c.id)
            return
            
    tg.cbq_handler(open_ad_lots_list, lambda c: c.data.startswith(f"{CBT.AD_LOTS_LIST}:"))
    tg.cbq_handler(open_fp_lots_list, lambda c: c.data.startswith(f"{CBT.FP_LOTS_LIST}:"))
    tg.cbq_handler(act_add_lot_manually, lambda c: c.data.startswith(f"{CBT.ADD_AD_TO_LOT_MANUALLY}:"))
    tg.msg_handler(add_lot_manually,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.ADD_AD_TO_LOT_MANUALLY))

    tg.cbq_handler(open_gf_list, lambda c: c.data.startswith(f"{CBT.PRODUCTS_FILES_LIST}:"))

    tg.cbq_handler(act_create_gf, lambda c: c.data == CBT.CREATE_PRODUCTS_FILE)
    tg.msg_handler(create_gf, func=lambda m: tg.check_state(m.chat.id, m.from_user.id,
                                                            CBT.CREATE_PRODUCTS_FILE))

    tg.cbq_handler(open_edit_lot_cp, lambda c: c.data.startswith(f"{CBT.EDIT_AD_LOT}:"))

    tg.cbq_handler(act_edit_delivery_text, lambda c: c.data.startswith(f"{CBT.EDIT_LOT_DELIVERY_TEXT}:"))
    tg.msg_handler(edit_delivery_text,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.EDIT_LOT_DELIVERY_TEXT))

    tg.cbq_handler(act_link_gf, lambda c: c.data.startswith(f"{CBT.BIND_PRODUCTS_FILE}:"))
    tg.msg_handler(link_gf, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.BIND_PRODUCTS_FILE))

    tg.cbq_handler(switch_lot_setting, lambda c: c.data.startswith("switch_lot:"))
    tg.cbq_handler(create_lot_delivery_test, lambda c: c.data.startswith("test_auto_delivery:"))
    tg.cbq_handler(del_lot, lambda c: c.data.startswith(f"{CBT.DEL_AD_LOT}:"))

    tg.cbq_handler(add_ad_to_lot, lambda c: c.data.startswith(f"{CBT.ADD_AD_TO_LOT}:"))
    tg.cbq_handler(update_funpay_lots_list, lambda c: c.data.startswith("update_funpay_lots:"))

    tg.cbq_handler(open_gf_settings, lambda c: c.data.startswith(f"{CBT.EDIT_PRODUCTS_FILE}:"))

    tg.cbq_handler(act_add_products_to_file, lambda c: c.data.startswith(f"{CBT.ADD_PRODUCTS_TO_FILE}:"))
    tg.msg_handler(add_products_to_file,
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.ADD_PRODUCTS_TO_FILE))

    tg.cbq_handler(send_products_file, lambda c: c.data.startswith("download_products_file:"))
    tg.cbq_handler(ask_del_products_file, lambda c: c.data.startswith("del_products_file:"))
    tg.cbq_handler(del_products_file, lambda c: c.data.startswith("confirm_del_products_file:"))


BIND_TO_PRE_INIT = [init_auto_delivery_cp]

# END OF FILE FunPayCortex/tg_bot/auto_delivery_cp.py