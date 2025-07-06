# FunPayCortex/tg_bot/statistics_cp.py
from __future__ import annotations
import json
import time
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import os
from threading import Thread

from FunPayAPI.common.enums import OrderStatuses
from FunPayAPI.common.utils import RegularExpressions
from FunPayAPI.updater.events import NewMessageEvent, OrderStatusChangedEvent
from FunPayAPI.types import MessageTypes

from locales.localizer import Localizer
from tg_bot import CBT, keyboards as kb, utils
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from telebot.types import CallbackQuery, Message

if TYPE_CHECKING:
    from cortex import Cortex

localizer = Localizer()
_t = localizer.translate  # Используем _t для избежания конфликтов
logger = logging.getLogger("FPC.statistics_cp")

SALES_HISTORY_FILE = "storage/cache/sales_history.json"
WITHDRAWAL_FORECAST_FILE = "storage/cache/withdrawal_forecast.json"

# ЗАГРУЗКА И СОХРАНЕНИЕ ДАННЫХ
def load_data(cortex: Cortex):
    base_path = cortex.base_path
    # Загрузка истории продаж
    history_path = os.path.join(base_path, SALES_HISTORY_FILE)
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                cortex.sales_history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            cortex.sales_history = []
    else:
        cortex.sales_history = []

    # Загрузка прогноза вывода
    forecast_path = os.path.join(base_path, WITHDRAWAL_FORECAST_FILE)
    if os.path.exists(forecast_path):
        try:
            with open(forecast_path, "r", encoding="utf-8") as f:
                cortex.withdrawal_forecast = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            cortex.withdrawal_forecast = {}
    else:
        cortex.withdrawal_forecast = {}

def save_data(cortex: Cortex):
    base_path = cortex.base_path
    history_path = os.path.join(base_path, SALES_HISTORY_FILE)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(cortex.sales_history, f, ensure_ascii=False, indent=2)

    forecast_path = os.path.join(base_path, WITHDRAWAL_FORECAST_FILE)
    with open(forecast_path, "w", encoding="utf-8") as f:
        json.dump(cortex.withdrawal_forecast, f, ensure_ascii=False, indent=2)

# ФОНОВОЕ ОБНОВЛЕНИЕ
def update_sales_history(cortex: Cortex, is_initial_scan: bool = False):
    """
    Получает только новые продажи и добавляет их в историю.
    """
    existing_order_ids = {sale['id'] for sale in cortex.sales_history}
    
    if is_initial_scan and cortex.telegram and list(cortex.telegram.authorized_users.keys()):
        cortex.telegram.bot.send_message(list(cortex.telegram.authorized_users.keys())[0],
                                         "📊 Началось первичное сканирование истории продаж. Это может занять некоторое время...")

    new_sales = []
    stop_fetching = False
    next_order_id, batch, locale, subcs = cortex.account.get_sales()

    while True:
        if not batch:
            break
            
        for sale in batch:
            if sale.id in existing_order_ids:
                stop_fetching = True
                break
            new_sales.append(sale)
        
        if stop_fetching or not next_order_id:
            break
            
        time.sleep(1)
        next_order_id, batch, locale, subcs = cortex.account.get_sales(start_from=next_order_id, locale=locale, sudcategories=subcs)

    if new_sales:
        new_sales_dicts = [
            {"id": s.id, "status": s.status.name, "price": s.price, "currency": str(s.currency), "timestamp": int(s.date.timestamp()), "description": s.description}
            for s in reversed(new_sales) # Добавляем в правильном хронологическом порядке
        ]
        cortex.sales_history = new_sales_dicts + cortex.sales_history
        save_data(cortex)
    
    if is_initial_scan and cortex.telegram and list(cortex.telegram.authorized_users.keys()):
        cortex.telegram.bot.send_message(list(cortex.telegram.authorized_users.keys())[0],
                                         f"✅ Сканирование истории продаж завершено. Загружено {len(cortex.sales_history)} заказов.")


def periodic_sales_update(cortex: Cortex):
    load_data(cortex)
    
    if not cortex.initial_scan_complete:
        update_sales_history(cortex, is_initial_scan=True)
        cortex.initial_scan_complete = True
    else:
        update_sales_history(cortex)
    
    report_interval_hours = cortex.MAIN_CFG["Statistics"].getint("report_interval", 0)
    if report_interval_hours <= 0:
        return # Авто-отчеты выключены

    last_report_time = time.time()
    while True:
        if time.time() - last_report_time >= report_interval_hours * 3600:
            update_sales_history(cortex)
            
            try:
                cortex.balance = cortex.get_balance()
            except Exception as e:
                logger.error(f"Не удалось обновить баланс для периодического отчета: {e}")

            # Отправка отчета
            period_days = cortex.MAIN_CFG["Statistics"].getint("analysis_period", 30)
            stats_data = calculate_stats(cortex.sales_history, period_days)
            msg = format_stats_message(cortex, f"{period_days} дн.", stats_data)
            cortex.telegram.send_notification(f"📊 <b>Ежедневный отчет по статистике:</b>\n\n{msg}")

            last_report_time = time.time()
        time.sleep(60 * 30) # Проверка каждые 30 минут

# ЛОГИКА СТАТИСТИКИ
def calculate_stats(sales_history: list, period_days: int | None):
    stats = {
        "sales_count": 0, "sales_sum": {},
        "refund_count": 0, "refund_sum": {},
        "sold_items": {}
    }
    now = datetime.now()
    
    for sale in sales_history:
        sale_date = datetime.fromtimestamp(sale["timestamp"])
        # Если указан период, и продажа старше этого периода - пропускаем её.
        if period_days is not None and (now - sale_date).days >= period_days:
            continue

        currency = sale["currency"]
        price = float(sale["price"])
        
        if sale["status"] == OrderStatuses.CLOSED.name:
            stats["sales_count"] += 1
            stats["sales_sum"][currency] = stats["sales_sum"].get(currency, 0) + price
            description = sale.get("description")
            if description:
                stats["sold_items"][description] = stats["sold_items"].get(description, 0) + 1
        elif sale["status"] == OrderStatuses.REFUNDED.name:
            stats["refund_count"] += 1
            stats["refund_sum"][currency] = stats["refund_sum"].get(currency, 0) + price
    return stats

def format_price_summary(price_dict: dict) -> str:
    if not price_dict:
        return "0 ¤"
    return ", ".join([f"{value:,.2f} {currency}".replace(",", " ") for currency, value in sorted(price_dict.items())])

def format_stats_message(cortex: Cortex, period_name: str, stats: dict) -> str:
    # Прогноз вывода
    now = time.time()
    forecast = {"hour": {}, "day": {}, "2day": {}}
    modified = False
    for order_id, data in cortex.withdrawal_forecast.copy().items():
        if now - data["time"] > 172800: # 48 часов
            del cortex.withdrawal_forecast[order_id]
            modified = True
            continue
        
        currency = data["currency"]
        price = data["price"]
        
        if now - data["time"] < 3600: # Меньше часа
            forecast["hour"][currency] = forecast["hour"].get(currency, 0) + price
        if now - data["time"] < 86400: # Меньше дня
            forecast["day"][currency] = forecast["day"].get(currency, 0) + price
        if now - data["time"] < 172800: # Меньше двух дней
            forecast["2day"][currency] = forecast["2day"].get(currency, 0) + price
            
    if modified:
        save_data(cortex)
    
    # Расчет суммы ожидающих заказов
    pending_sum = {}
    pending_count = 0
    try:
        # Получаем актуальный список заказов
        next_id_unused, sales, locale_unused, subcs_unused = cortex.account.get_sales(include_closed=False, include_refunded=False)
        for order in sales:
            if order.status == OrderStatuses.PAID:
                pending_count += 1
                currency_str = str(order.currency)
                pending_sum[currency_str] = pending_sum.get(currency_str, 0) + order.price
    except Exception as e:
        logger.error(f"Не удалось получить заказы для статистики: {e}")

    pending_sum_str = format_price_summary(pending_sum)
    unconfirmed_text = f"⏳ <b><u>Неподтвержденные:</u></b> {pending_count} шт. (на {pending_sum_str})\n\n" if pending_count > 0 else ""

    # Топ-5 продаваемых товаров
    top_items_text = ""
    if stats.get("sold_items"):
        sorted_items = sorted(stats["sold_items"].items(), key=lambda item: item[1], reverse=True)
        top_5 = sorted_items[:5]
        if top_5:
            top_items_list = [f"  ▫️ <i>{utils.escape(item_name)}</i> - <code>{count} шт.</code>" for item_name, count in top_5]
            top_items_text = "\n\n⭐ <b><u>Топ продаж:</u></b>\n" + "\n".join(top_items_list)

    return f"""
📊 <b>Статистика за {period_name}</b>

💰 <b><u>Финансы:</u></b>
- <b>Баланс:</b> <code>{cortex.balance.total_rub:,.2f} ₽, {cortex.balance.total_usd:,.2f} $, {cortex.balance.total_eur:,.2f} €</code>
- <b>К выводу:</b> <code>{cortex.balance.available_rub:,.2f} ₽, {cortex.balance.available_usd:,.2f} $, {cortex.balance.available_eur:,.2f} €</code>

{unconfirmed_text}⏳ <b><u>Прогноз поступлений:</u></b>
- <b>~ через час:</b> +{format_price_summary(forecast['hour'])}
- <b>~ через день:</b> +{format_price_summary(forecast['day'])}
- <b>~ через 2 дня:</b> +{format_price_summary(forecast['2day'])}

📈 <b><u>Продажи:</u></b>
- <b>Количество:</b> <code>{stats['sales_count']} шт.</code>
- <b>Сумма:</b> {format_price_summary(stats['sales_sum'])}

📉 <b><u>Возвраты:</u></b>
- <b>Количество:</b> <code>{stats['refund_count']} шт.</code>
- <b>Сумма:</b> {format_price_summary(stats['refund_sum'])}
{top_items_text}

⏱️ {_t('gl_last_update')}: <code>{datetime.now().strftime('%H:%M:%S')}</code>
    """.replace(",", " ")

# ОБРАБОТЧИКИ TELEGRAM
def init_statistics_cp(cortex: Cortex, *args):
    tg = cortex.telegram
    bot = tg.bot

    def open_statistics_menu(c: CallbackQuery):
        user_role = utils.get_user_role(tg.authorized_users, c.from_user.id)
        if user_role == 'manager' and not cortex.MAIN_CFG["ManagerPermissions"].getboolean("can_view_stats"):
            bot.answer_callback_query(c.id, _t("admin_only_command"), show_alert=True)
            return

        period_key = c.data.split(":")[1]
        
        if period_key == "main":
            bot.edit_message_text("📊 Меню статистики. Выберите период:", c.message.chat.id, c.message.id,
                                  reply_markup=kb.statistics_menu(cortex))
            bot.answer_callback_query(c.id)
            return

        periods = {"day": 1, "week": 7, "month": 30, "all": None}
        period_days = periods.get(period_key)

        stats_data = calculate_stats(cortex.sales_history, period_days)
        msg_text = format_stats_message(cortex, period_key.capitalize(), stats_data)
        
        bot.edit_message_text(msg_text, c.message.chat.id, c.message.id, reply_markup=kb.statistics_menu(cortex))
        bot.answer_callback_query(c.id)

    def open_statistics_config(c: CallbackQuery):
        action = c.data.split(":")[1]
        if action == "main":
            bot.edit_message_text("⚙️ Настройки статистики", c.message.chat.id, c.message.id,
                                  reply_markup=kb.statistics_config_menu(cortex))
        elif action == "set_period":
            result = bot.send_message(c.message.chat.id, "🔢 Введите новый период анализа в днях:", reply_markup=CLEAR_STATE_BTN())
            tg.set_state(c.message.chat.id, result.id, c.from_user.id, f"{CBT.STATS_CONFIG_MENU}:set_period")
        elif action == "set_interval":
            result = bot.send_message(c.message.chat.id, "⏰ Введите интервал для авто-отчета в часах (0 для отключения):", reply_markup=CLEAR_STATE_BTN())
            tg.set_state(c.message.chat.id, result.id, c.from_user.id, f"{CBT.STATS_CONFIG_MENU}:set_interval")
        bot.answer_callback_query(c.id)
    
    def set_analysis_period(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        try:
            days = int(m.text.strip())
            if days <= 0: raise ValueError
            cortex.MAIN_CFG.set("Statistics", "analysis_period", str(days))
            cortex.save_config(cortex.MAIN_CFG, os.path.join(cortex.base_path, "configs/_main.cfg"))
            bot.send_message(m.chat.id, f"✅ Период анализа изменен на {days} дн.", reply_markup=kb.statistics_config_menu(cortex))
        except ValueError:
            bot.send_message(m.chat.id, "❌ Неверное значение. Введите целое положительное число.")
            
    def set_report_interval(m: Message):
        tg.clear_state(m.chat.id, m.from_user.id, True)
        try:
            hours = int(m.text.strip())
            if hours < 0: raise ValueError
            cortex.MAIN_CFG.set("Statistics", "report_interval", str(hours))
            cortex.save_config(cortex.MAIN_CFG, os.path.join(cortex.base_path, "configs/_main.cfg"))
            bot.send_message(m.chat.id, f"✅ Интервал авто-отчетов изменен.", reply_markup=kb.statistics_config_menu(cortex))
        except ValueError:
            bot.send_message(m.chat.id, "❌ Неверное значение. Введите целое число (0 или больше).")
            
    tg.cbq_handler(open_statistics_menu, lambda c: c.data.startswith(f"{CBT.STATS_MENU}:"))
    tg.cbq_handler(open_statistics_config, lambda c: c.data.startswith(f"{CBT.STATS_CONFIG_MENU}:"))
    tg.msg_handler(set_analysis_period, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, f"{CBT.STATS_CONFIG_MENU}:set_period"))
    tg.msg_handler(set_report_interval, func=lambda m: tg.check_state(m.chat.id, m.from_user.id, f"{CBT.STATS_CONFIG_MENU}:set_interval"))

def order_status_hook(cortex: Cortex, event: OrderStatusChangedEvent):
    """
    Обновляет локальную историю при изменении статуса заказа.
    """
    order_id = event.order.id
    for sale in cortex.sales_history:
        if sale["id"] == order_id:
            sale["status"] = event.order.status.name
            break
    save_data(cortex)

def withdrawal_forecast_hook(cortex: Cortex, event: NewMessageEvent):
    """
    Отслеживает подтвержденные заказы для прогноза вывода средств.
    """
    if event.message.type not in [MessageTypes.ORDER_CONFIRMED, MessageTypes.ORDER_CONFIRMED_BY_ADMIN,
                                  MessageTypes.ORDER_REOPENED, MessageTypes.REFUND, MessageTypes.REFUND_BY_ADMIN]:
        return

    order_id_match = RegularExpressions().ORDER_ID.findall(str(event.message))
    if not order_id_match: return
    order_id = order_id_match[0][1:]

    if event.message.type in [MessageTypes.ORDER_REOPENED, MessageTypes.REFUND, MessageTypes.REFUND_BY_ADMIN]:
        if order_id in cortex.withdrawal_forecast:
            del cortex.withdrawal_forecast[order_id]
    else: # ORDER_CONFIRMED or ORDER_CONFIRMED_BY_ADMIN
        order = cortex.get_order_from_object(event.message)
        if not order or order.buyer_id == cortex.account.id:
            return
        cortex.withdrawal_forecast[order_id] = {"time": int(time.time()), "price": order.sum, "currency": str(order.currency)}
    
    save_data(cortex)

BIND_TO_PRE_INIT = [init_statistics_cp]
BIND_TO_ORDER_STATUS_CHANGED = [order_status_hook]
BIND_TO_NEW_MESSAGE = [withdrawal_forecast_hook]