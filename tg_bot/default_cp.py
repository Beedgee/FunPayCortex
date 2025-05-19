"""
В данном модуле описаны функции для ПУ настроек прокси.
Модуль реализован в виде плагина.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cortex import Cortex # Renamed FPCortex to Cortex
from telebot.types import CallbackQuery, Message # Message не используется, можно убрать
import logging # logging не используется, можно убрать

from locales.localizer import Localizer

# logger не используется, можно убрать
# logger = logging.getLogger("TGBot")
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
        translated_text = _(c.data, language=localizer.current_language) # Пытаемся перевести
        # Если перевод не изменил строку (т.е. ключ не найден), и строка не является числом (CBT константы)
        # и не является очевидным колбеком (содержит ":"), то показываем как есть
        # Это предотвратит показ "непереведенных" CBT констант или сложных колбеков как текста.
        if translated_text == c.data and not c.data.isdigit() and ":" not in c.data:
            # Если это просто текст, который не ключ локализации - можно показать его
             bot.answer_callback_query(c.id, text=c.data, show_alert=True)
        elif translated_text != c.data : # Если перевод успешен
             bot.answer_callback_query(c.id, text=translated_text, show_alert=True)
        else: # Если это CBT или сложный колбек, на который нет перевода - лучше ничего не показывать или дать стандартный ответ
            bot.answer_callback_query(c.id) # Пустой ответ, чтобы убрать "часики"
            # Или можно: bot.answer_callback_query(c.id, _("unknown_action", language=localizer.current_language), show_alert=True)
            # для "unknown_action" = "Неизвестное действие"


    tg.cbq_handler(default_callback_answer, lambda c: True)


BIND_TO_PRE_INIT = [init_default_cp]