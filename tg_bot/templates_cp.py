"""
В данном модуле описаны функции для ПУ шаблонами ответа.
Модуль реализован в виде плагина.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from Utils.cardinal_tools import safe_text # Используется для безопасной замены $username

if TYPE_CHECKING:
    from cardinal import Cortex # Renamed FPCortex to Cortex

from tg_bot import utils, keyboards, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery
import logging

from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def init_templates_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def check_template_exists(template_index: int, message_obj: Message | CallbackQuery) -> bool:
        # tmplt_not_found_err, gl_refresh уже локализованы
        chat_id = message_obj.chat.id if isinstance(message_obj, Message) else message_obj.message.chat.id
        message_id = message_obj.id if isinstance(message_obj, Message) else message_obj.message.id
        
        if template_index >= len(cortex_instance.telegram.answer_templates): # Используем >=
            update_button = K().add(B(_("gl_refresh"), callback_data=f"{CBT.TMPLT_LIST}:0"))
            bot.edit_message_text(_("tmplt_not_found_err", template_index), chat_id, message_id,
                                  reply_markup=update_button)
            return False
        return True

    def open_templates_list(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        # desc_tmplt уже локализован
        bot.edit_message_text(_("desc_tmplt"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.templates_list(cortex_instance, offset))
        bot.answer_callback_query(c.id)

    def open_templates_list_in_ans_mode(c: CallbackQuery):
        split_data = c.data.split(":")
        offset, node_id, username, prev_page_str = int(split_data[1]), int(split_data[2]), split_data[3], split_data[4]
        prev_page = int(prev_page_str)
        extra_data = split_data[5:] # Остальные части - это extra
        
        # Клавиатура уже использует локализацию
        bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                      reply_markup=keyboards.templates_list_ans_mode(cortex_instance, offset, node_id,
                                                                                     username, prev_page, extra_data))
        bot.answer_callback_query(c.id) # Отвечаем на колбэк

    def open_edit_template_cp(c: CallbackQuery):
        split_data = c.data.split(":")
        template_index, offset_str = int(split_data[1]), split_data[2]
        offset = int(offset_str)
        
        if not check_template_exists(template_index, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        keyboard_edit = keyboards.edit_template(cortex_instance, template_index, offset) # Клавиатура уже обновлена
        template_text = cortex_instance.telegram.answer_templates[template_index]
        
        # Добавим заголовок для ясности
        # Ключ tmplt_editing_header = "📝 Редактирование шаблона:"
        message_to_send = f"{_('tmplt_editing_header', language=localizer.current_language)}\n\n<code>{utils.escape(template_text)}</code>"
        bot.edit_message_text(message_to_send, c.message.chat.id, c.message.id, reply_markup=keyboard_edit)
        bot.answer_callback_query(c.id)

    def act_add_template(c: CallbackQuery):
        offset = int(c.data.split(":")[1])
        variables = ["v_username", "v_photo", "v_sleep"] # v_list уже локализован
        # V_new_template (с большой V) уже локализован
        text_prompt = f"{_('V_new_template')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result = bot.send_message(c.message.chat.id, text_prompt, reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.ADD_TMPLT, {"offset": offset})
        bot.answer_callback_query(c.id)

    def add_template(m: Message):
        state_data = tg.get_state(m.chat.id, m.from_user.id)
        offset = state_data["data"]["offset"] if state_data and state_data.get("data") else 0
        tg.clear_state(m.chat.id, m.from_user.id, True)
        
        new_template_text = m.text.strip()

        if not new_template_text: # Проверка на пустой ввод
            # Добавим ключ tmplt_err_empty_text = "❌ Текст шаблона не может быть пустым."
            bot.reply_to(m, _("tmplt_err_empty_text", language=localizer.current_language), 
                         reply_markup=K().row(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"),
                                            B(_("tmplt_add_another"), callback_data=f"{CBT.ADD_TMPLT}:{offset}")))
            return

        if new_template_text in tg.answer_templates:
            # tmplt_already_exists_err, gl_back, tmplt_add_another уже локализованы
            error_keyboard = K().row(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"),
                                     B(_("tmplt_add_another"), callback_data=f"{CBT.ADD_TMPLT}:{offset}"))
            bot.reply_to(m, _("tmplt_already_exists_err"), reply_markup=error_keyboard)
            return

        tg.answer_templates.append(new_template_text)
        utils.save_answer_templates(tg.answer_templates) # Сохраняем обновленный список
        # log_tmplt_added уже локализован
        logger.info(_("log_tmplt_added", m.from_user.username, m.from_user.id, new_template_text))

        # tmplt_add_more, tmplt_added уже локализованы
        keyboard_success = K().row(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"),
                                   B(_("tmplt_add_more"), callback_data=f"{CBT.ADD_TMPLT}:{offset}"))
        bot.reply_to(m, _("tmplt_added"), reply_markup=keyboard_success)

    def del_template(c: CallbackQuery):
        split_data = c.data.split(":")
        template_index_to_delete, offset_str = int(split_data[1]), split_data[2]
        offset = int(offset_str)
        
        if not check_template_exists(template_index_to_delete, c): # Передаем CallbackQuery
            bot.answer_callback_query(c.id)
            return

        deleted_template_text = tg.answer_templates.pop(template_index_to_delete) # Удаляем и получаем текст
        utils.save_answer_templates(tg.answer_templates) # Сохраняем изменения
        # log_tmplt_deleted уже локализован
        logger.info(_("log_tmplt_deleted", c.from_user.username, c.from_user.id, deleted_template_text))
        
        # Корректируем offset для отображения списка
        new_offset = max(0, offset - MENU_CFG.TMPLT_BTNS_AMOUNT if offset >= MENU_CFG.TMPLT_BTNS_AMOUNT and len(tg.answer_templates) < offset + MENU_CFG.TMPLT_BTNS_AMOUNT else offset)
        new_offset = 0 if len(tg.answer_templates) <= MENU_CFG.TMPLT_BTNS_AMOUNT else new_offset
        
        # desc_tmplt уже локализован
        bot.edit_message_text(_("desc_tmplt"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.templates_list(cortex_instance, new_offset))
        # Добавим ключ tmplt_deleted_successfully = "Шаблон '{template_text}' успешно удален."
        bot.answer_callback_query(c.id, _("tmplt_deleted_successfully", template_text=utils.escape(deleted_template_text[:30]+"...") if len(deleted_template_text) > 30 else utils.escape(deleted_template_text), language=localizer.current_language) , show_alert=True)

    def send_template(c: CallbackQuery):
        split_data = c.data.split(":")
        template_index, node_id, username, prev_page_str = (int(split_data[1]), int(split_data[2]), 
                                                             split_data[3], split_data[4])
        prev_page = int(prev_page_str)
        extra_data_for_back_button = split_data[5:]

        if template_index >= len(tg.answer_templates): # Проверка на выход за пределы списка
            # tmplt_not_found_err уже локализован
            bot.send_message(c.message.chat.id, _("tmplt_not_found_err", template_index),
                             message_thread_id=c.message.message_thread_id if c.message.is_topic_message else None) # Учитываем топики
            
            # Восстанавливаем предыдущую клавиатуру
            reply_kb_after_error = None
            if prev_page == 0: # Новый ответ (1)
                reply_kb_after_error = keyboards.reply(node_id, username, False, bool(int(extra_data_for_back_button[0])) if extra_data_for_back_button else False)
            elif prev_page == 1: # Новый ответ (2)
                reply_kb_after_error = keyboards.reply(node_id, username, True, bool(int(extra_data_for_back_button[0])) if extra_data_for_back_button else False)
            elif prev_page == 2: # Меню заказа
                order_id_for_back = extra_data_for_back_button[0]
                no_refund_flag_for_back = bool(int(extra_data_for_back_button[1]))
                reply_kb_after_error = keyboards.new_order(order_id_for_back, username, node_id, no_refund=no_refund_flag_for_back)
            
            if reply_kb_after_error:
                 bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=reply_kb_after_error)
            bot.answer_callback_query(c.id)
            return

        template_to_send = tg.answer_templates[template_index]
        # Безопасная замена $username
        text_with_username = template_to_send.replace("$username", safe_text(username))
        
        send_success = cortex_instance.send_message(node_id, text_with_username, username)

        if prev_page == 3: # Если это был просто предпросмотр/отправка без возврата в сложное меню
            # msg_sent_short, msg_sending_error_short уже локализованы
            bot.answer_callback_query(c.id, _("msg_sent_short") if send_success else _("msg_sending_error_short"), show_alert=True) # show_alert для наглядности
            # Удаляем сообщение со списком шаблонов, так как действие завершено
            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            return
        else: # Если нужно вернуть клавиатуру ответа/заказа
            # msg_tmplt_msg_sent, msg_sending_error уже локализованы
            result_message_text = _("tmplt_msg_sent", node_id, username, utils.escape(text_with_username)) if send_success else \
                                  _("msg_sending_error", node_id, username)
            # Отправляем новое сообщение с результатом и клавиатурой "ответить еще"
            # Старую клавиатуру со списком шаблонов удалять не будем, пользователь сам закроет или она заменится
            bot.send_message(c.message.chat.id, result_message_text,
                             reply_markup=keyboards.reply(node_id, username, again=True, extend=True), # extend=True по умолчанию после отправки
                             message_thread_id=c.message.message_thread_id if c.message.is_topic_message else None)
        bot.answer_callback_query(c.id) # Отвечаем на колбэк, чтобы убрать часики

    # Регистрация хэндлеров (без изменений)
    tg.cbq_handler(open_templates_list, lambda c: c.data.startswith(f"{CBT.TMPLT_LIST}:"))
    tg.cbq_handler(open_templates_list_in_ans_mode, lambda c: c.data.startswith(f"{CBT.TMPLT_LIST_ANS_MODE}:"))
    tg.cbq_handler(open_edit_template_cp, lambda c: c.data.startswith(f"{CBT.EDIT_TMPLT}:"))
    tg.cbq_handler(act_add_template, lambda c: c.data.startswith(f"{CBT.ADD_TMPLT}:"))
    tg.msg_handler(add_template, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.ADD_TMPLT))
    tg.cbq_handler(del_template, lambda c: c.data.startswith(f"{CBT.DEL_TMPLT}:"))
    tg.cbq_handler(send_template, lambda c: c.data.startswith(f"{CBT.SEND_TMPLT}:"))


BIND_TO_PRE_INIT = [init_templates_cp]