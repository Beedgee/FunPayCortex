# tg_bot/order_control_cp.py

from __future__ import annotations
from typing import TYPE_CHECKING
import time
import logging
from threading import Thread
from datetime import datetime

from FunPayAPI.types import OrderStatuses
from tg_bot import utils, keyboards as kb, CBT
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from locales.localizer import Localizer

if TYPE_CHECKING:
    from cortex import Cortex
    from telebot.types import CallbackQuery, Message

logger = logging.getLogger("FPC.order_control")
localizer = Localizer()
_ = localizer.translate


def periodic_order_check(cortex: Cortex):
    """Фоновый процесс для проверки "зависших" заказов."""
    logger.info("Цикл проверки зависших заказов запущен.")
    while True:
        try:
            now_ts = int(time.time())

            # Проверка заказов, ожидающих выполнения
            if cortex.MAIN_CFG.getboolean("OrderControl", "notify_pending_execution", fallback=False):
                threshold_seconds = cortex.MAIN_CFG.getint("OrderControl", "pending_execution_threshold_m", fallback=60) * 60
                threshold_minutes = threshold_seconds // 60
                if cortex.runner and cortex.runner.saved_orders:
                    for order in cortex.runner.saved_orders.values():
                        if order.status == OrderStatuses.PAID and (now_ts - order.date.timestamp()) > threshold_seconds:
                            if order.id not in cortex.order_confirmations or \
                               cortex.order_confirmations[order.id].get("notified_pending_execution") is not True:
                                
                                logger.info(f"Обнаружен зависший заказ #{order.id}, ожидающий выполнения.")
                                chat = cortex.account.get_chat_by_name(order.buyer_username, True)
                                text = _("oc_notify_pending_execution_msg", order_id=order.id, username=utils.escape(order.buyer_username)).format(threshold_minutes)
                                kb_markup = kb.new_order(order.id, order.buyer_username, chat.id if chat else 0, cortex=cortex)
                                cortex.telegram.send_notification(text, kb_markup, notification_type=utils.NotificationTypes.other)
                                
                                if order.id not in cortex.order_confirmations:
                                    cortex.order_confirmations[order.id] = {}
                                cortex.order_confirmations[order.id]["notified_pending_execution"] = True
                                cortex._save_order_confirmations()

            # Проверка заказов, ожидающих подтверждения
            if cortex.MAIN_CFG.getboolean("OrderControl", "notify_pending_confirmation", fallback=False):
                threshold_seconds = cortex.MAIN_CFG.getint("OrderControl", "pending_confirmation_threshold_h", fallback=24) * 3600
                threshold_hours = threshold_seconds // 3600
                if cortex.runner and cortex.runner.saved_orders:
                    for order in cortex.runner.saved_orders.values():
                        if order.status != OrderStatuses.PAID:
                            continue

                        # Если заказ был отмечен, используем точное время. Иначе - время создания заказа.
                        confirmation_start_ts = cortex.order_confirmations.get(order.id, {}).get("confirmed_ts", order.date.timestamp())

                        # Проверяем, не было ли уже уведомление
                        if cortex.order_confirmations.get(order.id, {}).get("notified_pending_confirmation"):
                            continue

                        if (now_ts - confirmation_start_ts) > threshold_seconds:
                            logger.info(f"Обнаружен зависший заказ #{order.id}, ожидающий подтверждения.")
                            chat = cortex.account.get_chat_by_name(order.buyer_username, True)
                            text = _("oc_notify_pending_confirmation_msg", order_id=order.id, username=utils.escape(order.buyer_username)).format(threshold_hours)
                            kb_markup = kb.new_order(order.id, order.buyer_username, chat.id if chat else 0, cortex=cortex)
                            cortex.telegram.send_notification(text, kb_markup, notification_type=utils.NotificationTypes.other)

                            if order.id not in cortex.order_confirmations:
                                cortex.order_confirmations[order.id] = {}
                            cortex.order_confirmations[order.id]["notified_pending_confirmation"] = True
                            cortex._save_order_confirmations()

        except KeyError as e:
            if str(e) == "'OrderControl'":
                logger.error("Секция [OrderControl] не найдена в конфиге. Проверка заказов приостановлена. Добавьте секцию и перезапустите бота.")
                time.sleep(3600)  # Ждем час перед следующей попыткой, чтобы не спамить в лог
            else:
                logger.error(f"Ошибка в цикле проверки заказов (KeyError): {e}")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(15 * 60)
        except Exception as e:
            logger.error(f"Ошибка в цикле проверки заказов: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            time.sleep(15 * 60)
        
        # Пауза 15 минут
        time.sleep(15 * 60)


def init_order_control_cp(cortex: Cortex, *args):
    """Инициализация модуля 'Контроль заказов'."""
    tg = cortex.telegram
    bot = tg.bot

    # Запускаем фоновый процесс
    checker_thread = Thread(target=periodic_order_check, args=(cortex,), daemon=True)
    checker_thread.start()

    def open_order_control_settings(c: CallbackQuery):
        """Открывает меню настроек Контроля заказов."""
        kb_markup = kb.order_control_settings(cortex)
        bot.edit_message_text(_("oc_menu_desc"), c.message.chat.id, c.message.id, reply_markup=kb_markup)
        bot.answer_callback_query(c.id)

    def mark_order_delivered(c: CallbackQuery):
        """Обработчик нажатия кнопки 'Товар выдан'."""
        order_id = c.data.split(":")[1]
        
        if order_id not in cortex.order_confirmations:
            cortex.order_confirmations[order_id] = {}
        
        cortex.order_confirmations[order_id]["confirmed_ts"] = int(time.time())
        cortex._save_order_confirmations()
        
        logger.info(f"Заказ #{order_id} отмечен как выполненный.")
        bot.answer_callback_query(c.id, _("oc_alert_marked_as_delivered"), show_alert=True)
        
        # Обновляем клавиатуру, чтобы убрать кнопку
        try:
            order = cortex.runner.saved_orders.get(order_id)
            if order:
                 chat = cortex.account.get_chat_by_name(order.buyer_username, True)
                 new_kb = kb.new_order(order.id, order.buyer_username, chat.id if chat else 0, cortex=cortex)
                 bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=new_kb)
        except Exception as e:
            logger.warning(f"Не удалось обновить клавиатуру для заказа #{order_id} после отметки о выдаче: {e}")

    def act_set_exec_threshold(c: CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("oc_prompt_exec_threshold"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.OC_SET_EXEC_THRESHOLD)
        bot.answer_callback_query(c.id)

    def set_exec_threshold(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        try:
            threshold = int(m.text)
            if threshold <= 0: raise ValueError
            cortex.MAIN_CFG.set("OrderControl", "pending_execution_threshold_m", str(threshold))
            cortex.save_config(cortex.MAIN_CFG, "configs/_main.cfg")
            kb_markup = kb.order_control_settings(cortex)
            bot.send_message(m.chat.id, _("oc_success_threshold_changed", threshold), reply_markup=kb_markup)
        except ValueError:
            bot.reply_to(m, _("oc_err_threshold_format"))

    def act_set_confirm_threshold(c: CallbackQuery):
        result = bot.send_message(c.message.chat.id, _("oc_prompt_confirm_threshold"), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, CBT.OC_SET_CONFIRM_THRESHOLD)
        bot.answer_callback_query(c.id)

    def set_confirm_threshold(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        try:
            threshold = int(m.text)
            if threshold <= 0: raise ValueError
            cortex.MAIN_CFG.set("OrderControl", "pending_confirmation_threshold_h", str(threshold))
            cortex.save_config(cortex.MAIN_CFG, "configs/_main.cfg")
            kb_markup = kb.order_control_settings(cortex)
            bot.send_message(m.chat.id, _("oc_success_threshold_changed", threshold), reply_markup=kb_markup)
        except ValueError:
            bot.reply_to(m, _("oc_err_threshold_format"))

    # Регистрируем обработчики
    tg.cbq_handler(open_order_control_settings, lambda c: c.data == f"{CBT.CATEGORY}:orc")
    tg.cbq_handler(act_set_exec_threshold, lambda c: c.data == CBT.OC_SET_EXEC_THRESHOLD)
    tg.msg_handler(set_exec_threshold, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.OC_SET_EXEC_THRESHOLD))
    tg.cbq_handler(act_set_confirm_threshold, lambda c: c.data == CBT.OC_SET_CONFIRM_THRESHOLD)
    tg.msg_handler(set_confirm_threshold, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.OC_SET_CONFIRM_THRESHOLD))
    tg.cbq_handler(mark_order_delivered, lambda c: c.data.startswith(f"{CBT.MARK_ORDER_DELIVERED}:"))


BIND_TO_POST_INIT = [init_order_control_cp]