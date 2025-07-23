# START OF FILE FunPayCortex-main/handlers.py

"""
В данном модуле написаны хэндлеры для разных эвентов.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex

from FunPayAPI.types import OrderShortcut, Order, Currency, OrderStatuses
from FunPayAPI import exceptions, utils as fp_utils
from FunPayAPI.updater.events import *
from FunPayAPI.common.enums import SubCategoryTypes

from tg_bot import utils, keyboards, statistics_cp, crm_cp
from Utils import cortex_tools
from locales.localizer import Localizer
from threading import Thread
import configparser
from datetime import datetime
import logging
import time
import re

LAST_STACK_ID = ""
MSG_LOG_LAST_STACK_ID = ""

logger = logging.getLogger("FPC.handlers")
localizer = Localizer()
_ = localizer.translate

ORDER_HTML_TEMPLATE = """<a href="https://funpay.com/orders/DELITEST/" class="tc-item">
   <div class="tc-date" bis_skin_checked="1">
      <div class="tc-date-time" bis_skin_checked="1">сегодня, $date</div>
      <div class="tc-date-left" bis_skin_checked="1">только что</div>
   </div>
   <div class="tc-order" bis_skin_checked="1">#DELITEST</div>
   <div class="order-desc" bis_skin_checked="1">
      <div bis_skin_checked="1">$lot_name</div>
      <div class="text-muted" bis_skin_checked="1">Автовыдача, Тест</div>
   </div>
   <div class="tc-user" bis_skin_checked="1">
      <div class="media media-user offline" bis_skin_checked="1">
         <div class="media-left" bis_skin_checked="1">
            <div class="avatar-photo pseudo-a" tabindex="0" data-href="https://funpay.com/users/000000/" style="background-image: url(/img/layout/avatar.png);" bis_skin_checked="1"></div>
         </div>
         <div class="media-body" bis_skin_checked="1">
            <div class="media-user-name" bis_skin_checked="1">
               <span class="pseudo-a" tabindex="0" data-href="https://funpay.com/users/000000/">$username</span>
            </div>
            <div class="media-user-status" bis_skin_checked="1">был 1.000.000 лет назад</div>
         </div>
      </div>
   </div>
   <div class="tc-status text-primary" bis_skin_checked="1">Оплачен</div>
   <div class="tc-price text-nowrap tc-seller-sum" bis_skin_checked="1">999999.0 <span class="unit">₽</span></div>
</a>"""


# INIT MESSAGE
def save_init_chats_handler(c: Cortex, e: InitialChatEvent):
    """
    Кэширует существующие чаты (чтобы не отправлять приветственные сообщения).
    """
    if c.MAIN_CFG["Greetings"].getboolean("sendGreetings") and e.chat.id not in c.old_users:
        c.old_users[e.chat.id] = int(time.time())
        cortex_tools.cache_old_users(c.old_users)


# NEW MESSAGE / LAST CHAT MESSAGE CHANGED
def old_log_msg_handler(c: Cortex, e: LastChatMessageChangedEvent):
    """
    Логирует полученное сообщение.
    """
    if not c.old_mode_enabled:
        return
    text, chat_name, chat_id = str(e.chat), e.chat.name, e.chat.id
    username = e.account.username if not e.chat.unread else e.chat.name

    logger.info(_("log_new_msg", chat_name, chat_id) + f" (аккаунт: {e.account_name})")
    for index, line in enumerate(text.split("\n")):
        if not index:
            logger.info(f"$MAGENTA└───> $YELLOW{username}: $CYAN{line}")
        else:
            logger.info(f"      $CYAN{line}")


def log_msg_handler(c: Cortex, e: NewMessageEvent):
    global MSG_LOG_LAST_STACK_ID
    if e.stack.id() == MSG_LOG_LAST_STACK_ID:
        return

    chat_name, chat_id = e.message.chat_name, e.message.chat_id

    logger.info(_("log_new_msg", chat_name, chat_id) + f" (аккаунт: {e.account_name})")
    for index, event in enumerate(e.stack.get_stack()):
        username, text = event.message.author, event.message.text or event.message.image_link
        for line_index, line in enumerate(text.split("\n")):
            if not index and not line_index:
                logger.info(f"$MAGENTA└───> $YELLOW{username}: $CYAN{line}")
            elif not line_index:
                logger.info(f"      $YELLOW{username}: $CYAN{line}")
            else:
                logger.info(f"      $CYAN{line}")
    MSG_LOG_LAST_STACK_ID = e.stack.id()


def greetings_handler(c: Cortex, e: NewMessageEvent | LastChatMessageChangedEvent):
    """
    Отправляет приветственное сообщение.
    """
    if not c.MAIN_CFG["Greetings"].getboolean("sendGreetings"):
        return
    if not c.old_mode_enabled:
        if isinstance(e, LastChatMessageChangedEvent):
            return
        obj = e.message
        chat_id, chat_name, mtype, its_me, badge = obj.chat_id, obj.chat_name, obj.type, obj.author_id == e.account.id, obj.badge
    else:
        obj = e.chat
        chat_id, chat_name, mtype, its_me, badge = obj.id, obj.name, obj.last_message_type, not obj.unread, None

    # Проверяем, нужно ли приветствовать этого пользователя.
    if any([time.time() - c.old_users.get(chat_id, 0) < float(
            c.MAIN_CFG["Greetings"]["greetingsCooldown"]) * 24 * 60 * 60,
            its_me, mtype in (MessageTypes.DEAR_VENDORS, MessageTypes.ORDER_CONFIRMED_BY_ADMIN), badge is not None,
            (mtype is not MessageTypes.NON_SYSTEM and c.MAIN_CFG["Greetings"].getboolean("ignoreSystemMessages"))]):
        return

    # Немедленно обновляем временную метку, чтобы предотвратить повторную отправку
    c.old_users[chat_id] = int(time.time())
    cortex_tools.cache_old_users(c.old_users)

    logger.info(_("log_sending_greetings", chat_name, chat_id) + f" (аккаунт: {e.account_name})")
    text = cortex_tools.format_msg_text(c.MAIN_CFG["Greetings"]["greetingsText"], obj)
    Thread(target=c.send_message, args=(e.account, chat_id, text, chat_name), daemon=True).start()


def send_response_handler(c: Cortex, e: NewMessageEvent | LastChatMessageChangedEvent):
    """
    Проверяет, является ли сообщение командой, и если да, отправляет ответ на данную команду.
    """
    if not c.autoresponse_enabled:
        return
    if not c.old_mode_enabled:
        if isinstance(e, LastChatMessageChangedEvent):
            return
        obj, mtext = e.message, str(e.message)
        chat_id, chat_name, username = e.message.chat_id, e.message.chat_name, e.message.author
    else:
        obj, mtext = e.chat, str(e.chat)
        chat_id, chat_name, username = obj.id, obj.name, obj.name

    mtext = mtext.replace("\n", "")
    if any([c.bl_response_enabled and username in c.blacklist, (command := mtext.strip().lower()) not in c.AR_CFG]):
        return

    logger.info(_("log_new_cmd", command, chat_name, chat_id) + f" (аккаунт: {e.account_name})")
    response_text = cortex_tools.format_msg_text(c.AR_CFG[command]["response"], obj)
    Thread(target=c.send_message, args=(e.account, chat_id, response_text, chat_name), daemon=True).start()


def old_send_new_msg_notification_handler(c: Cortex, e: LastChatMessageChangedEvent):
    if any([not c.old_mode_enabled, not c.telegram, not e.chat.unread,
            c.bl_msg_notification_enabled and e.chat.name in c.blacklist,
            e.chat.last_message_type is not MessageTypes.NON_SYSTEM, str(e.chat).strip().lower() in c.AR_CFG.sections(),
            str(e.chat).startswith("!автовыдача")]):
        return
    
    sender_link = f"<a href=\"https://funpay.com/users/{e.chat.interlocutor_id}/\">{utils.escape(e.chat.name)}</a>"
    receiver_link = f"<a href=\"https://funpay.com/users/{e.account.id}/\">{utils.escape(e.account.username)}</a>"

    text = f"<b>[{e.account_name}]</b> {sender_link} => {receiver_link}:\n<code>{utils.escape(str(e.chat))}</code>"
    kb = keyboards.reply(e.chat.id, e.chat.name, extend=True, account_name=e.account_name)
    Thread(target=c.telegram.send_notification, args=(text, kb, utils.NotificationTypes.new_message),
           daemon=True).start()


def send_new_msg_notification_handler(c: Cortex, e: NewMessageEvent) -> None:
    """
    Отправляет уведомление о новом сообщении в телеграм.
    """
    global LAST_STACK_ID
    if not c.telegram or e.stack.id() == LAST_STACK_ID:
        return
    LAST_STACK_ID = e.stack.id()

    chat_id, chat_name = e.message.chat_id, e.message.chat_name
    if c.bl_msg_notification_enabled and chat_name in c.blacklist:
        return

    events = []
    nm, m, f, b = False, False, False, False
    for i in e.stack.get_stack():
        if i.message.author_id == 0:
            if c.include_fp_msg_enabled:
                events.append(i)
                f = True
        elif i.message.by_bot:
            if c.include_bot_msg_enabled:
                events.append(i)
                b = True
        elif i.message.author_id == e.account.id:
            if c.include_my_msg_enabled:
                events.append(i)
                m = True
        else:
            events.append(i)
            nm = True
    if not events:
        return

    if [m, f, b, nm].count(True) == 1 and \
            any([m and not c.only_my_msg_enabled, f and not c.only_fp_msg_enabled, b and not c.only_bot_msg_enabled]):
        return

    text = f"<b>[{e.account_name}]</b>\n"
    last_message_author_id = -1
    
    for i in e.stack.get_stack():
        message = i.message
        
        # Формируем ссылки на профили
        sender_id = message.author_id
        sender_name = message.author
        receiver_id = e.account.id if sender_id != e.account.id else message.interlocutor_id
        receiver_name = e.account.username if sender_id != e.account.id else message.chat_name
        
        # Для системных сообщений отправитель - FunPay
        if sender_id == 0:
            sender_link = f"<i><b>FunPay</b></i>"
        else:
            sender_link = f"<a href=\"https://funpay.com/users/{sender_id}/\">{utils.escape(sender_name)}</a>"
        
        receiver_link = f"<a href=\"https://funpay.com/users/{receiver_id}/\">{utils.escape(receiver_name)}</a>"

        if message.author_id != last_message_author_id:
             text += f"{sender_link} => {receiver_link}\n"
        
        msg_text = f"<code>{utils.escape(message.text)}</code>" if message.text else \
            f"<a href=\"{message.image_link}\">" \
            f"{c.show_image_name and not (message.author_id == e.account.id and message.by_bot) and message.image_name or _('photo')}</a>"
        text += f"{msg_text}\n"
        last_message_author_id = message.author_id
    
    text += "\n"

    # Обогащение уведомления данными из CRM
    if e.message.interlocutor_id and e.message.interlocutor_id in c.crm_data:
        customer_data = c.crm_data[e.message.interlocutor_id]
        purchase_count = len(customer_data.get("purchases", []))
        refund_count = len(customer_data.get("refunds", []))
        pending_count = len(customer_data.get("pending", []))
        notes = customer_data.get("notes", "")

        crm_info = f"<b><a href='https://funpay.com/users/{e.message.interlocutor_id}/'>Картотека клиента</a></b>\n"
        crm_info += f"✅ Покупок: <code>{purchase_count}</code>"
        if pending_count > 0:
            crm_info += f" | ⏳ Ожидает: <code>{pending_count}</code>"
        if refund_count > 0:
            crm_info += f" | 💸 Возвратов: <code>{refund_count}</code>"
        if notes:
            crm_info += f"\n📝 Заметка: <i>{utils.escape(notes)}</i>"
        text += crm_info

    kb = keyboards.reply(chat_id, chat_name, extend=True, account_name=e.account_name)
    Thread(target=c.telegram.send_notification, args=(text, kb, utils.NotificationTypes.new_message),
           daemon=True).start()


def send_review_notification(c: Cortex, account: FunPayAPI.Account, order: Order, chat_id: int, reply_text: str | None):
    if not c.telegram:
        return
    reply_text = _("ntfc_review_reply_text").format(utils.escape(reply_text)) if reply_text else ""
    text = f"<b>[{account.name}]</b> " + _("ntfc_new_review").format('⭐' * order.review.stars, order.id, utils.escape(order.review.text), reply_text)
    Thread(target=c.telegram.send_notification,
           args=(text,
                 keyboards.new_order(order.id, order.buyer_username, chat_id, account_name=account.name),
                 utils.NotificationTypes.review),
           daemon=True).start()


def process_review_handler(c: Cortex, e: NewMessageEvent | LastChatMessageChangedEvent):
    if not c.old_mode_enabled:
        if isinstance(e, LastChatMessageChangedEvent):
            return
        obj = e.message
        message_type, its_me = obj.type, obj.i_am_buyer
        message_text, chat_id = str(obj), obj.chat_id

    else:
        obj = e.chat
        message_type, its_me = obj.last_message_type, f" {e.account.username} " in str(obj)
        message_text, chat_id = str(obj), obj.id

    if message_type not in [types.MessageTypes.NEW_FEEDBACK, types.MessageTypes.FEEDBACK_CHANGED] or its_me:
        return

    def send_reply():
        try:
            order = c.get_order_from_object(e.account, obj)
            if order is None:
                raise Exception("Не удалось получить объект заказа.")
        except:
            logger.error(f"Не удалось получить информацию о заказе для сообщения: \"{message_text}\". (аккаунт: {e.account_name})")
            logger.debug("TRACEBACK", exc_info=True)
            return

        if not order.review or not order.review.stars:
            return

        logger.info(f"Изменен отзыв на заказ #{order.id}. (аккаунт: {e.account_name})")

        toggle = f"star{order.review.stars}Reply"
        text_key = f"star{order.review.stars}ReplyText"
        reply_text = None
        if c.MAIN_CFG["ReviewReply"].getboolean(toggle) and c.MAIN_CFG["ReviewReply"].get(text_key):
            try:
                def format_text4review(text_: str):
                    max_l = 999
                    text_ = text_[:max_l + 1]
                    if len(text_) > max_l:
                        ln = len(text_)
                        indexes = []
                        for char in (".", "!", "\n"):
                            index1 = text_.rfind(char)
                            indexes.extend([index1, text_[:index1].rfind(char)])
                        text_ = text_[:max(indexes, key=lambda x: (x < ln - 1, x))] + "🧠"
                    text_ = text_.strip()
                    while text_.count("\n") > 9 and text.count("\n\n") > 1:
                        text_ = text_[::-1].replace("\n\n", "\n",
                                                    min([text_.count("\n\n") - 1, text_.count("\n") - 9]))[::-1]
                    if text_.count("\n") > 9:
                        text_ = text_[::-1].replace("\n", " ", text_.count("\n") - 9)[::-1]
                    return text_

                reply_text = cortex_tools.format_order_text(c.MAIN_CFG["ReviewReply"].get(text_key), order)
                reply_text = format_text4review(reply_text)
                e.account.send_review(order.id, reply_text)
            except:
                logger.error(f"Произошла ошибка при ответе на отзыв {order.id}. (аккаунт: {e.account_name})")
                logger.debug("TRACEBACK", exc_info=True)
        send_review_notification(c, e.account, order, chat_id, reply_text)

    Thread(target=send_reply, daemon=True).start()


def send_command_notification_handler(c: Cortex, e: NewMessageEvent | LastChatMessageChangedEvent):
    """
    Отправляет уведомление о введенной команде в телеграм.
    """
    if not c.telegram:
        return
    if not c.old_mode_enabled:
        if isinstance(e, LastChatMessageChangedEvent):
            return
        obj, message_text = e.message, str(e.message)
        chat_id, chat_name, username = e.message.chat_id, e.message.chat_name, e.message.author
    else:
        obj, message_text = e.chat, str(e.chat)
        chat_id, chat_name, username = obj.id, obj.name, obj.name if obj.unread else e.account.username

    if c.bl_cmd_notification_enabled and username in c.blacklist:
        return
    command = message_text.strip().lower()
    if command not in c.AR_CFG or not c.AR_CFG[command].getboolean("telegramNotification"):
        return

    if not c.AR_CFG[command].get("notificationText"):
        text = f"<b>[{e.account_name}]</b> 🧑‍💻 Пользователь <b><i>{username}</i></b> ввел команду <code>{utils.escape(command)}</code>."
    else:
        text = f"<b>[{e.account_name}]</b> " + cortex_tools.format_msg_text(c.AR_CFG[command]["notificationText"], obj)

    Thread(target=c.telegram.send_notification, args=(text, keyboards.reply(chat_id, chat_name, account_name=e.account_name),
                                                      utils.NotificationTypes.command), daemon=True).start()


def test_auto_delivery_handler(c: Cortex, e: NewMessageEvent | LastChatMessageChangedEvent):
    """
    Выполняет тест автовыдачи.
    """
    if not c.old_mode_enabled:
        if isinstance(e, LastChatMessageChangedEvent):
            return
        obj, message_text, chat_name, chat_id = e.message, str(e.message), e.message.chat_name, e.message.chat_id
    else:
        obj, message_text, chat_name, chat_id = e.chat, str(e.chat), e.chat.name, e.chat.id

    if not message_text.startswith("!автовыдача"):
        return

    split = message_text.split()
    if len(split) < 2:
        logger.warning("Одноразовый ключ автовыдачи не обнаружен.")
        return

    key = split[1].strip()
    if key not in c.delivery_tests:
        logger.warning("Невалидный одноразовый ключ автовыдачи.")
        return

    lot_name = c.delivery_tests[key]
    del c.delivery_tests[key]
    date = datetime.now()
    date_text = date.strftime("%H:%M")
    html = ORDER_HTML_TEMPLATE.replace("$username", chat_name).replace("$lot_name", lot_name).replace("$date",
                                                                                                      date_text)

    fake_order = OrderShortcut("ADTEST", lot_name, 0.0, Currency.UNKNOWN, chat_name, 000000, chat_id,
                               types.OrderStatuses.PAID,
                               date, "Авто-выдача, Тест", None, html)

    fake_event = NewOrderEvent(e.account, e.runner_tag, fake_order)
    c.run_handlers(c.new_order_handlers, (c, fake_event,))


def send_categories_raised_notification_handler(c: Cortex, cat: types.Category, error_text: str = "", account: FunPayAPI.Account | None = None) -> None:
    """
    Отправляет уведомление о поднятии лотов в Telegram.
    """
    if not c.telegram or not account:
        return

    text = f"<b>[{account.name}]</b> ⤴️<b><i>Поднял все лоты категории</i></b> <code>{cat.name}</code>\n<tg-spoiler>{error_text}</tg-spoiler>"""
    Thread(target=c.telegram.send_notification,
           args=(text,),
           kwargs={"notification_type": utils.NotificationTypes.lots_raise}, daemon=True).start()


# Изменен список ордеров (REGISTER_TO_ORDERS_LIST_CHANGED)
def get_lot_config_by_name(c: Cortex, name: str) -> configparser.SectionProxy | None:
    """
    Ищет секцию лота в конфиге автовыдачи.

    :param c: объект кортекса.
    :param name: название лота.

    :return: секцию конфига или None.
    """
    for i in c.AD_CFG.sections():
        if i in name:
            return c.AD_CFG[i]
    return None


def check_products_amount(config_obj: configparser.SectionProxy) -> int:
    file_name = config_obj.get("productsFileName")
    if not file_name:
        return 1
    return cortex_tools.count_products(f"storage/products/{file_name}")


def update_profile_lots_handler(c: Cortex, e: OrdersListChangedEvent):
    """Обновляет лоты в профиле аккаунта."""
    logger.info(f"Получаю информацию о лотах для аккаунта '{e.account_name}'...")
    attempts = 3
    while attempts:
        try:
            e.account.profile = e.account.get_user(e.account.id)
            break
        except:
            logger.error(f"Произошла ошибка при получении информации о лотах (аккаунт: {e.account_name}).")
            logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            time.sleep(2)
    else:
        logger.error(f"Не удалось получить информацию о лотах (аккаунт: {e.account_name}): превышено кол-во попыток.")
        return


# Новый ордер (REGISTER_TO_NEW_ORDER)
def log_new_order_handler(c: Cortex, e: NewOrderEvent, *args):
    """
    Логирует новый заказ.
    """
    logger.info(f"Новый заказ! ID: $YELLOW#{e.order.id}$RESET (аккаунт: {e.account_name})")


def setup_event_attributes_handler(c: Cortex, e: NewOrderEvent, *args):
    config_section_name = None
    config_section_obj = None
    lot_description = e.order.description
    
    # пробуем найти лот, чтобы не выдавать по строке, которую вписал покупатель при оформлении заказа
    if e.account.profile:
        for lot in sorted(list(e.account.profile.get_sorted_lots(2).get(e.order.subcategory, {}).values()),
                          key=lambda l: len(f"{l.server}, {l.description}"), reverse=True):
            if lot.server and lot.description:
                temp_desc = f"{lot.server}, {lot.description}"
            elif lot.server:
                temp_desc = lot.server
            else:
                temp_desc = lot.description

            if temp_desc in e.order.description:
                lot_description = temp_desc
                break

    for i in range(3):
        for lot_name in c.AD_CFG:
            if i == 0:
                rule = lot_description == lot_name
            elif i == 1:
                rule = lot_description.startswith(lot_name)
            else:
                rule = lot_name in lot_description

            if rule:
                config_section_obj = c.AD_CFG[lot_name]
                config_section_name = lot_name
                break
        if config_section_obj:
            break

    attributes = {"config_section_name": config_section_name, "config_section_obj": config_section_obj,
                  "delivered": False, "delivery_text": None, "goods_delivered": 0, "goods_left": None,
                  "error": 0, "error_text": None}
    for i in attributes:
        setattr(e, i, attributes[i])

    if config_section_obj is None:
        logger.info(f"Лот не найден в конфиге авто-выдачи! (аккаунт: {e.account_name})")
    else:
        logger.info(f"Лот найден в конфиге авто-выдачи! (аккаунт: {e.account_name})")


def send_new_order_notification_handler(c: Cortex, e: NewOrderEvent, *args):
    """
    Отправляет уведомления о новом заказе в телеграм.
    """
    if not c.telegram:
        return
    if e.order.buyer_username in c.blacklist and c.MAIN_CFG["BlockList"].getboolean("blockNewOrderNotification"):
        return
    if not (config_obj := getattr(e, "config_section_obj")):
        delivery_info = _("ntfc_new_order_not_in_cfg")
    else:
        if not c.autodelivery_enabled:
            delivery_info = _("ntfc_new_order_ad_disabled")
        elif config_obj.getboolean("disable"):
            delivery_info = _("ntfc_new_order_ad_disabled_for_lot")
        elif c.bl_delivery_enabled and e.order.buyer_username in c.blacklist:
            delivery_info = _("ntfc_new_order_user_blocked")
        else:
            delivery_info = _("ntfc_new_order_will_be_delivered")

    seller_price_str = f"{e.order.price:.2f}"
    buyer_price = None

    if e.order.subcategory:
        try:
            calc_result = e.account.calc(e.order.subcategory.type, e.order.subcategory.id, e.order.price)
            buyer_prices_in_order_currency = [m.price for m in calc_result.methods if m.currency == e.order.currency]
            if buyer_prices_in_order_currency:
                buyer_price = min(buyer_prices_in_order_currency)
        except Exception as ex:
            logger.warning(f"Не удалось рассчитать комиссию для заказа #{e.order.id} (аккаунт: {e.account_name}): {ex}")
            logger.debug("TRACEBACK", exc_info=True)

    if buyer_price is None:
        buyer_price = e.order.price

    buyer_price_text = f"{buyer_price:.2f}"

    price_details = _("ntfc_new_order_price_details", seller_price=seller_price_str,
                      buyer_price=buyer_price_text, currency=str(e.order.currency))

    text = f"<b>[{e.account_name}]</b> " + _("ntfc_new_order_no_link", f"{utils.escape(e.order.description)}, {utils.escape(e.order.subcategory_name)}",
             e.order.buyer_username, price_details, e.order.id, delivery_info)

    chat = e.account.get_chat_by_name(e.order.buyer_username, True)
    if chat:
        chat_id = chat.id
        keyboard = keyboards.new_order(e.order.id, e.order.buyer_username, chat_id, account_name=e.account_name, cortex=c)
        Thread(target=c.telegram.send_notification, args=(text, keyboard, utils.NotificationTypes.new_order),
               daemon=True).start()
    else:
        logger.warning(f"Не удалось найти чат для пользователя {e.order.buyer_username} для отправки уведомления о заказе #{e.order.id} (аккаунт: {e.account_name})")


def deliver_goods(c: Cortex, e: NewOrderEvent, *args):
    chat = e.account.get_chat_by_name(e.order.buyer_username, True)
    if not chat:
        logger.error(f"Не удалось найти чат с покупателем {e.order.buyer_username} для выдачи товара по заказу #{e.order.id} (аккаунт: {e.account_name}).")
        setattr(e, "error", 1)
        setattr(e, "error_text", f"Не найден чат с покупателем {e.order.buyer_username}.")
        return

    chat_id = chat.id
    cfg_obj = getattr(e, "config_section_obj")
    delivery_text = cortex_tools.format_order_text(cfg_obj["response"], e.order)

    amount, goods_left, products = 1, -1, []
    try:
        if file_name := cfg_obj.get("productsFileName"):
            if c.multidelivery_enabled and not cfg_obj.getboolean("disableMultiDelivery"):
                amount = e.order.amount if e.order.amount else 1
            products, goods_left = cortex_tools.get_products(f"storage/products/{file_name}", amount)
            delivery_text = delivery_text.replace("$product", "\n".join(products).replace("\\n", "\n"))
    except Exception as exc:
        logger.error(
            f"Произошла ошибка при получении товаров для заказа $YELLOW{e.order.id}$RESET (аккаунт: {e.account_name}): {str(exc)}")
        logger.debug("TRACEBACK", exc_info=True)
        setattr(e, "error", 1)
        setattr(e, "error_text",
                f"Произошла ошибка при получении товаров для заказа {e.order.id}: {str(exc)}")
        return

    result = c.send_message(e.account, chat_id, delivery_text, e.order.buyer_username)
    if not result:
        logger.error(f"Не удалось отправить товар для ордера $YELLOW{e.order.id}$RESET (аккаунт: {e.account_name}).")
        setattr(e, "error", 1)
        setattr(e, "error_text", f"Не удалось отправить сообщение с товаром для заказа {e.order.id}.")
        if file_name and products:
            cortex_tools.add_products(f"storage/products/{file_name}", products, at_zero_position=True)
    else:
        logger.info(f"Товар для заказа {e.order.id} выдан. (аккаунт: {e.account_name})")
        setattr(e, "delivered", True)
        setattr(e, "delivery_text", delivery_text)
        setattr(e, "goods_delivered", amount)
        setattr(e, "goods_left", goods_left)


def deliver_product_handler(c: Cortex, e: NewOrderEvent, *args) -> None:
    """
    Обертка для deliver_product(), обрабатывающая ошибки.
    """
    if not c.MAIN_CFG["FunPay"].getboolean("autoDelivery"):
        return
    if e.order.buyer_username in c.blacklist and c.bl_delivery_enabled:
        logger.info(f"Пользователь {e.order.buyer_username} находится в ЧС и включена блокировка автовыдачи. "
                    f"$YELLOW(ID: {e.order.id}, аккаунт: {e.account_name})$RESET")
        return

    if (config_section_obj := getattr(e, "config_section_obj")) is None:
        return
    if config_section_obj.getboolean("disable"):
        logger.info(f"Для лота \"{e.order.description}\" отключена автовыдача. (аккаунт: {e.account_name})")
        return

    c.run_handlers(c.pre_delivery_handlers, (c, e))
    deliver_goods(c, e, *args)
    c.run_handlers(c.post_delivery_handlers, (c, e))


# REGISTER_TO_POST_DELIVERY
def send_delivery_notification_handler(c: Cortex, e: NewOrderEvent):
    """
    Отправляет уведомление в телеграм об отправке товара.
    """
    if c.telegram is None:
        return

    if getattr(e, "error"):
        text = f"<b>[{e.account_name}]</b> ❌ <code>{getattr(e, 'error_text')}</code>"
    else:
        amount = "<b>∞</b>" if getattr(e, "goods_left") == -1 else f"<code>{getattr(e, 'goods_left')}</code>"
        text = f"""<b>[{e.account_name}]</b> ✅ Успешно выдал товар для ордера <code>{e.order.id}</code>.\n
🛒 <b><i>Товар:</i></b>
<code>{utils.escape(getattr(e, "delivery_text"))}</code>\n
📋 <b><i>Осталось товаров: </i></b>{amount}"""

    Thread(target=c.telegram.send_notification, args=(text,),
           kwargs={"notification_type": utils.NotificationTypes.delivery}, daemon=True).start()


def update_lot_state(account: FunPayAPI.Account, lot: types.LotShortcut, task: int) -> bool:
    """
    Обновляет состояние лота

    :param account: объект аккаунта.
    :param lot: объект лота.
    :param task: -1 - деактивировать лот. 1 - активировать лот.

    :return: результат выполнения.
    """
    attempts = 3
    while attempts:
        try:
            lot_fields = account.get_lot_fields(lot.id)
            if task == 1:
                lot_fields.active = True
                account.save_lot(lot_fields)
                logger.info(f"Восстановил лот $YELLOW{lot.description}$RESET (аккаунт: {account.name}).")
            elif task == -1:
                lot_fields.active = False
                account.save_lot(lot_fields)
                logger.info(f"Деактивировал лот $YELLOW{lot.description}$RESET (аккаунт: {account.name}).")
            return True
        except Exception as e:
            if isinstance(e, exceptions.RequestFailedError) and e.status_code == 404:
                logger.error(f"Произошла ошибка при изменении состояния лота $YELLOW{lot.description}$RESET (аккаунт: {account.name}): лот не найден.")
                return False
            logger.error(f"Произошла ошибка при изменении состояния лота $YELLOW{lot.description}$RESET (аккаунт: {account.name}).")
            logger.debug("TRACEBACK", exc_info=True)
            attempts -= 1
            time.sleep(2)
    logger.error(
        f"Не удалось изменить состояние лота $YELLOW{lot.description}$RESET (аккаунт: {account.name}): превышено кол-во попыток.")
    return False


def update_lots_states(cortex_instance: Cortex, account: FunPayAPI.Account):
    if not any([cortex_instance.autorestore_enabled, cortex_instance.autodisable_enabled]):
        return
    if not account.profile:
        logger.warning(f"Профиль для аккаунта {account.name} не загружен, пропуск обновления состояний лотов.")
        return

    all_lots = account.profile.get_sorted_lots(1)
    deactivated, restored = [], []
    
    for lot in all_lots.values():
        if not lot.description: continue
        
        current_task = 0
        config_obj = get_lot_config_by_name(cortex_instance, lot.description)

        if not lot.active:
            if config_obj is None:
                if cortex_instance.autorestore_enabled: current_task = 1
            else:
                if cortex_instance.autorestore_enabled and not config_obj.getboolean("disableAutoRestore"):
                    if not cortex_instance.autodisable_enabled or check_products_amount(config_obj):
                        current_task = 1
        else: # Лот активен
            if config_obj and not check_products_amount(config_obj) and \
               cortex_instance.autodisable_enabled and not config_obj.getboolean("disableAutoDisable"):
                current_task = -1

        if current_task:
            result = update_lot_state(account, lot, current_task)
            if result:
                if current_task == -1: deactivated.append(lot.description)
                elif current_task == 1: restored.append(lot.description)
            time.sleep(0.5)

    if deactivated and cortex_instance.telegram:
        lots_str = "\n".join(deactivated)
        text = f"<b>[{account.name}]</b> 🔴 <b>Деактивировал лоты:</b>\n\n<code>{utils.escape(lots_str)}</code>"
        Thread(target=cortex_instance.telegram.send_notification, args=(text,),
               kwargs={"notification_type": utils.NotificationTypes.lots_deactivate}, daemon=True).start()
    if restored and cortex_instance.telegram:
        lots_str = "\n".join(restored)
        text = f"<b>[{account.name}]</b> 🟢 <b>Активировал лоты:</b>\n\n<code>{utils.escape(lots_str)}</code>"
        Thread(target=cortex_instance.telegram.send_notification, args=(text,),
               kwargs={"notification_type": utils.NotificationTypes.lots_restore}, daemon=True).start()


def update_lots_state_handler(cortex_instance: Cortex, event: NewOrderEvent, *args):
    Thread(target=update_lots_states, args=(cortex_instance, event.account), daemon=True).start()


# BIND_TO_ORDER_STATUS_CHANGED
def send_thank_u_message_handler(c: Cortex, e: OrderStatusChangedEvent):
    """
    Отправляет ответное сообщение на подтверждение заказа.
    """
    if not c.MAIN_CFG["OrderConfirm"].getboolean("sendReply") or e.order.status is not types.OrderStatuses.CLOSED:
        return

    text = cortex_tools.format_order_text(c.MAIN_CFG["OrderConfirm"]["replyText"], e.order)
    chat = e.account.get_chat_by_name(e.order.buyer_username, True)
    logger.info(f"Пользователь $YELLOW{e.order.buyer_username}$RESET подтвердил выполнение заказа "
                f"$YELLOW{e.order.id}.$RESET (аккаунт: {e.account_name})")
    logger.info(f"Отправляю ответное сообщение ... (аккаунт: {e.account_name})")
    Thread(target=c.send_message, args=(e.account, chat.id, text, e.order.buyer_username),
           kwargs={'watermark': c.MAIN_CFG["OrderConfirm"].getboolean("watermark")}, daemon=True).start()


def send_order_confirmed_notification_handler(cortex_instance: Cortex, event: OrderStatusChangedEvent):
    """
    Отправляет уведомление о подтверждении заказа в Telegram.
    """
    if not event.order.status == types.OrderStatuses.CLOSED:
        return

    chat = event.account.get_chat_by_name(event.order.buyer_username, True)
    text = f"""<b>[{event.account_name}]</b> 🪙 Пользователь <a href="https://funpay.com/chat/?node={chat.id if chat else ''}">{event.order.buyer_username}</a> """ \
           f"""подтвердил выполнение заказа <code>{event.order.id}</code>. (<code>{event.order.price} {event.order.currency}</code>)"""
    Thread(target=cortex_instance.telegram.send_notification,
           args=(text,
                 keyboards.new_order(event.order.id, event.order.buyer_username, chat.id if chat else 0, account_name=event.account_name, cortex=cortex_instance),
                 utils.NotificationTypes.order_confirmed),
           daemon=True).start()


def send_bot_started_notification_handler(c: Cortex, *args):
    """
    Отправляет уведомление о запуске бота в телеграм.
    """
    if c.telegram is None:
        return

    full_text = f"✅ <b><u>FPCortex v{c.VERSION} инициализирован!</u></b>\n\n"
    total_balance = {"₽": 0.0, "$": 0.0, "€": 0.0}
    total_sales = 0

    for name, account in c.accounts.items():
        if account.balance:
            total_balance["₽"] += account.balance.total_rub
            total_balance["$"] += account.balance.total_usd
            total_balance["€"] += account.balance.total_eur
        if account.active_sales is not None:
            total_sales += account.active_sales
        
        full_text += f"👑 <b>{name}</b> (<code>{account.username}</code> | <code>{account.id}</code>)\n" \
                     f"  💰 <code>{account.balance.total_rub if account.balance else '?'}₽, {account.balance.total_usd if account.balance else '?'} $, {account.balance.total_eur if account.balance else '?'}€</code>\n" \
                     f"  📊 Активных заказов: <code>{account.active_sales if account.active_sales is not None else '?'}</code>\n\n"

    full_text += f"<b><u>Итог по всем аккаунтам:</u></b>\n" \
                 f"💰 <b>Общий баланс:</b> <code>{total_balance['₽']:.2f}₽, {total_balance['$']:.2f}$, {total_balance['€']:.2f}€</code>\n" \
                 f"📊 <b>Всего активных заказов:</b> <code>{total_sales}</code>\n\n" \
                 f"👨‍💻 <b><i>Автор:</i></b> @beedge"

    for chat_id, message_id in c.telegram.init_messages:
        try:
            c.telegram.bot.edit_message_text(full_text, chat_id, message_id)
        except:
            continue


BIND_TO_INIT_MESSAGE = [save_init_chats_handler,
                       crm_cp.crm_initial_chat_hook]

BIND_TO_LAST_CHAT_MESSAGE_CHANGED = [old_log_msg_handler,
                                     greetings_handler,
                                     send_response_handler,
                                     process_review_handler,
                                     old_send_new_msg_notification_handler,
                                     send_command_notification_handler,
                                     test_auto_delivery_handler]

BIND_TO_NEW_MESSAGE = [log_msg_handler,
                       greetings_handler,
                       send_response_handler,
                       process_review_handler,
                       send_new_msg_notification_handler,
                       send_command_notification_handler,
                       test_auto_delivery_handler,
                       statistics_cp.withdrawal_forecast_hook]

BIND_TO_POST_LOTS_RAISE = [send_categories_raised_notification_handler]

BIND_TO_ORDERS_LIST_CHANGED = [update_profile_lots_handler]

BIND_TO_NEW_ORDER = [log_new_order_handler, setup_event_attributes_handler,
                     send_new_order_notification_handler, deliver_product_handler,
                     update_lots_state_handler,
                     crm_cp.crm_new_order_hook]

BIND_TO_ORDER_STATUS_CHANGED = [send_thank_u_message_handler, send_order_confirmed_notification_handler,
                                statistics_cp.order_status_hook, crm_cp.crm_order_status_hook]

BIND_TO_POST_DELIVERY = [send_delivery_notification_handler]

BIND_TO_POST_START = [send_bot_started_notification_handler]
# END OF FILE FunPayCortex-main/handlers.py