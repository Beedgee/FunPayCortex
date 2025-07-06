# Файл: FunPayCortex-main/tg_bot/default_cp.py

# START OF FILE FunPayCortex/tg_bot/default_cp.py

"""
В данном модуле описаны функции для ПУ настроек прокси.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex
from telebot.types import CallbackQuery

from locales.localizer import Localizer

localizer = Localizer()
_ = localizer.translate


def init_default_cp(cortex_instance: Cortex, *args):
    tg = cortex_instance.telegram
    bot = tg.bot

    def default_callback_answer(c: CallbackQuery):
        """
        Отвечает на колбеки, которые не поймал ни один хендлер.
        Пытается перевести c.data, если такой ключ есть в локализации.
        Иначе, просто отвечает c.data (как было).
        """
        translated_text = _(c.data, language=localizer.current_language)
        if translated_text == c.data and not c.data.isdigit() and ":" not in c.data:
             bot.answer_callback_query(c.id, text=c.data, show_alert=True)
        elif translated_text != c.data :
             bot.answer_callback_query(c.id, text=translated_text, show_alert=True)
        else:
            bot.answer_callback_query(c.id, text=_("unknown_action"), show_alert=True)


    tg.cbq_handler(default_callback_answer, lambda c: True)


BIND_TO_POST_INIT = [init_default_cp]

# END OF FILE FunPayCortex/tg_bot/default_cp.py