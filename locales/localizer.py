# Файл: FunPayCortex-main/locales/localizer.py

from typing import Literal

from locales import ru, en, uk
import logging

logger = logging.getLogger("localizer")


class Localizer:
    def __new__(cls, curr_lang: str | None = None):
        if not hasattr(cls, "instance"):
            cls.instance = super(Localizer, cls).__new__(cls)
            cls.instance.languages = {
                "ru": ru,
                "en": en,
                "uk": uk
            }
            cls.instance.current_language = "ru"  # Устанавливаем язык по умолчанию
        if curr_lang in cls.instance.languages:
            cls.instance.current_language = curr_lang
        return cls.instance

    def _get_translation(self, variable_name: str, language: str):
        lang_module = self.languages.get(language)
        if lang_module and hasattr(lang_module, variable_name):
            return getattr(lang_module, variable_name)
        return None

    def translate(self, variable_name: str, *args, **kwargs):
        """
        Возвращает форматированный локализированный текст.

        :param variable_name: название переменной с текстом.
        :param args: позиционные аргументы для форматирования.
        :param kwargs: именованные аргументы для форматирования.

        :return: форматированный локализированный текст.
        """
        # Извлекаем язык из kwargs, если он там есть
        language = kwargs.pop('language', None)
        text = None

        # 1. Попробовать получить перевод для указанного языка
        if language:
            text = self._get_translation(variable_name, language)

        # 2. Если не получилось, попробовать для текущего языка
        if text is None:
            text = self._get_translation(variable_name, self.current_language)

        # 3. Если всё ещё нет, использовать русский как основной язык по умолчанию
        if text is None:
            text = self._get_translation(variable_name, "ru")
        
        # 4. Если и в русском нет, вернуть имя переменной
        if text is None:
            text = variable_name

        try:
            return text.format(*args, **kwargs)
        except (IndexError, KeyError) as e:
            # В случае ошибки форматирования, возвращаем исходный текст,
            # чтобы избежать падения программы.
            logger.debug(f"Ошибка форматирования для переменной '{variable_name}' с текстом '{text}' и аргументами {args}, {kwargs}: {e}", exc_info=True)
            return text


    def add_translation(self, uuid: str, variable_name: str, value: str, language: Literal["uk", "ru", "en"]):
        """Позволяет добавить перевод фраз из плагина."""
        setattr(self.languages[language], f"{uuid}_{variable_name}", value)

    def plugin_translate(self, uuid: str, variable_name: str, *args, **kwargs):
        """Позволяет получить перевод фраз из плагина."""
        # Сначала ищем переменную с префиксом UUID
        prefixed_variable_name = f"{uuid}_{variable_name}"
        
        # Передаем язык и другие kwargs в `translate`
        language = kwargs.get('language')
        translation = self.translate(prefixed_variable_name, *args, **kwargs)
        
        # Если перевод с префиксом не найден (возвращено имя переменной),
        # ищем перевод без префикса.
        if translation == prefixed_variable_name:
            return self.translate(variable_name, *args, **kwargs)
        
        return translation