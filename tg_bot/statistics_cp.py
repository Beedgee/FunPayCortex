# START OF FILE FunPayCortex-main/tg_bot/statistics_cp.py
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cortex import Cortex

from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup as K, InlineKeyboardButton as B
from tg_bot import CBT, keyboards, utils
from tg_bot.static_keyboards import CLEAR_STATE_BTN
from locales.localizer import Localizer

localizer = Localizer()
_ = localizer.translate

def init_statistics_cp(cortex: Cortex, *args):
    tg = cortex.telegram
    bot = tg.bot

    def open_stats_settings(c: CallbackQuery):
        """Открывает меню настроек статистики."""
        bot.edit_message_text(_("stat_settings_desc"), c.message.chat.id, c.message.id,
                              reply_markup=keyboards.statistics_settings(cortex, c.message.chat.id))
        bot.answer_callback_query(c.id)

    def toggle_chat_notification(c: CallbackQuery):
        """Включает/выключает уведомления для текущего чата."""
        chat_id_to_toggle = str(c.message.chat.id)
        chats_str = cortex.MAIN_CFG.get("Statistics", "notification_chats", fallback="")
        chats_list = [c_id.strip() for c_id in chats_str.split(",") if c_id.strip()]

        if chat_id_to_toggle in chats_list:
            chats_list.remove(chat_id_to_toggle)
        else:
            chats_list.append(chat_id_to_toggle)
        
        cortex.MAIN_CFG.set("Statistics", "notification_chats", ",".join(chats_list))
        cortex.save_config(cortex.MAIN_CFG, "configs/_main.cfg")
        
        c.data = CBT.STATS_SETTINGS
        open_stats_settings(c)

    def act_set_value(c: CallbackQuery):
        """Запрашивает новое значение для интервала или периода."""
        if c.data == CBT.STATS_SET_INTERVAL:
            prompt_key = "stat_prompt_interval"
            state_key = CBT.STATS_SET_INTERVAL
        elif c.data == CBT.STATS_SET_PERIOD:
            prompt_key = "stat_prompt_period"
            state_key = CBT.STATS_SET_PERIOD
        else:
            bot.answer_callback_query(c.id, _("unknown_action"), show_alert=True)
            return

        result = bot.send_message(c.message.chat.id, _(prompt_key), reply_markup=CLEAR_STATE_BTN())
        tg.set_state(c.message.chat.id, result.id, c.from_user.id, state_key)
        bot.answer_callback_query(c.id)

    def process_new_value(m: Message, param_name: str, min_value: int):
        """Обрабатывает введенное значение интервала или периода."""
        tg.clear_state(m.chat.id, m.from_user.id, True)
        try:
            new_value = int(m.text.strip())
            if new_value < min_value:
                raise ValueError(f"Value must be >= {min_value}")
        except ValueError:
            bot.reply_to(m, _("gl_error_try_again") + f" (введите целое число, не менее {min_value})")
            return

        cortex.MAIN_CFG.set("Statistics", param_name, str(new_value))
        cortex.save_config(cortex.MAIN_CFG, "configs/_main.cfg")
        
        keyboard_back = K().add(B(_("gl_back"), callback_data=CBT.STATS_SETTINGS))
        bot.reply_to(m, _("gl_yep"), reply_markup=keyboard_back)

    tg.cbq_handler(open_stats_settings, lambda c: c.data == CBT.STATS_SETTINGS)
    tg.cbq_handler(toggle_chat_notification, lambda c: c.data == CBT.STATS_TOGGLE_CHAT)
    tg.cbq_handler(act_set_value, lambda c: c.data in [CBT.STATS_SET_INTERVAL, CBT.STATS_SET_PERIOD])

    tg.msg_handler(lambda m: process_new_value(m, "notification_interval", 1), 
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.STATS_SET_INTERVAL))
    tg.msg_handler(lambda m: process_new_value(m, "parsing_period", 1),
                   func=lambda m: tg.check_state(m.chat.id, m.from_user.id, CBT.STATS_SET_PERIOD))

BIND_TO_PRE_INIT = [init_statistics_cp]