# START OF FILE FunPayCortex/locales/ru.py

# Глобальные
gl_next = "Далее ▶️"
gl_back = "Назад ◀️"
gl_yes = "Да ✅"
gl_yep = "Ага ✅"
gl_no = "Нет ❌"
gl_cancel = "Отмена 🚫"
gl_error = "Ошибка ⚠️"
gl_try_again = "Попробовать снова"
gl_error_try_again = f"{gl_error}. {gl_try_again}."
gl_refresh = "Обновить 🔄"
gl_delete = "Удалить 🗑️"
gl_edit = "Изменить ✏️"
gl_configure = "Настроить ⚙️"
gl_pcs = "шт."
gl_last_update = "Обновлено"
gl_refresh_and_try_again = "Обновите список и попробуйте снова."

# - Главное меню
mm_language = "🌍 Язык"
mm_global = "🔧 Общие настройки"
mm_notifications = "🔔 Уведомления"
mm_autoresponse = "🤖 Автоответчик"
mm_autodelivery = "📦 Автовыдача"
mm_blacklist = "🚫 Черный список"
mm_templates = "📝 Шаблоны ответов"
mm_greetings = "👋 Приветствия"
mm_order_confirm = "👍 Ответ на подтверждение"
mm_review_reply = "⭐ Ответ на отзывы"
mm_new_msg_view = "💬 Вид уведомлений"
mm_plugins = "🧩 Плагины"
mm_configs = "🔩 Конфигурации"
mm_authorized_users = "👤 Пользователи"
mm_proxy = "🌐 Прокси"

# Глобальные переключатели
gs_autoraise = "{} Авто-буст лотов"
gs_autoresponse = "{} Автоответчик"
gs_autodelivery = "{} Автовыдача"
gs_nultidelivery = "{} Мульти-выдача"
gs_autorestore = "{} Восстановление лотов"
gs_autodisable = "{} Деактивация лотов"
gs_old_msg_mode = "{} Устаревший режим сообщений"
gs_keep_sent_messages_unread = "{} Не отмечать прочитанным при отправке"

# Настройки уведомлений
ns_new_msg = "{} Новое сообщение"
ns_cmd = "{} Получена команда"
ns_new_order = "{} Новый заказ"
ns_order_confirmed = "{} Заказ подтвержден"
ns_lot_activate = "{} Лот восстановлен"
ns_lot_deactivate = "{} Лот деактивирован"
ns_delivery = "{} Товар выдан"
ns_raise = "{} Лоты подняты"
ns_new_review = "{} Новый отзыв"
ns_bot_start = "{} Бот запущен"
ns_other = "{} Другие (плагины)"

# Настройки автоответчика
ar_edit_commands = "✏️ Редактор команд"
ar_add_command = "➕ Новая команда"
ar_to_ar = "🤖 К настройкам автоответчика"
ar_to_mm = "Меню 🏠"
ar_edit_response = "✏️ Текст ответа"
ar_edit_notification = "✏️ Текст уведомления"
ar_notification = "{} Уведомление в Telegram"
ar_add_more = "➕ Еще"
ar_add_another = "➕ Другую"
ar_no_valid_commands_entered = "Не введено ни одной корректной команды."
ar_default_response_text = "Ответ для этой команды еще не настроен. Отредактируйте его."
ar_default_notification_text = "Пользователь $username ввел команду: $message_text"
ar_command_deleted_successfully = "Команда/сет «{command_name}» успешно удалена."

# Настройки авто-выдачи
ad_edit_autodelivery = "🗳️ Редактор автовыдачи"
ad_add_autodelivery = "➕ Привязать автовыдачу"
ad_add_another_ad = "➕ Привязать другой"
ad_add_more_ad = "➕ Привязать еще"
ad_edit_goods_file = "📋 Файлы товаров"
ad_upload_goods_file = "📤 Загрузить файл"
ad_create_goods_file = "➕ Создать файл"
ad_to_ad = "📦 К настройкам автовыдачи"
never_updated = "никогда"
ad_default_response_text_new_lot = "Спасибо за покупку, $username!\nВот твой товар:\n$product"

# - Редактировать авто-выдачу
ea_edit_delivery_text = "✏️ Текст выдачи"
ea_link_goods_file = "🔗 Привязать файл товаров"
ea_delivery = "{} Автовыдача"
ea_multidelivery = "{} Мультивыдача"
ea_restore = "{} Восстановление"
ea_deactivate = "{} Деактивация"
ea_test = "🔑 Тестовый ключ"
ea_more_test = "🔑 Еще ключ"
ea_link_another_gf = "🔗 Другой файл"

# - Добавить авто-выдачу
fl_manual = "✍️ Ввести вручную"

# - Товарные файли
gf_add_goods = "➕ Добавить товары"
gf_download = "📥 Скачать"
gf_create_another = "➕ Создать другой"
gf_create_more = "➕ Создать еще"
gf_add_more = "➕ Добавить еще"
gf_try_add_again = "➕ Повторить"
lot_info_header = "Информация о лоте"
text_not_set = "(текст не задан)"
gf_infinity = "бесконечно"
gf_count_error = "ошибка подсчета"
gf_file_not_found_short = "не найден"
gf_not_linked = "не привязан"
gf_file_created_now = "создан"
gf_file_creation_error_short = "ошибка создания"
no_lots_using_file = "Ни один лот не использует этот файл."
gf_no_products_to_add = "Не было введено товаров для добавления."
gf_deleted_successfully = "Файл «{file_name}» успешно удален."
gf_already_deleted = "Файл «{file_name}» уже был удален."


# Настройки черного списка
bl_autodelivery = "{} Не выдавать товар"
bl_autoresponse = "{} Не отвечать на команды"
bl_new_msg_notifications = "{} Без уведомлений о новых сообщениях"
bl_new_order_notifications = "{} Без уведомлений о новых заказах"
bl_command_notifications = "{} Без уведомлений о командах"

# Заготовки ответа
tmplt_add = "➕ Новый шаблон"
tmplt_add_more = "➕ Еще шаблон"
tmplt_add_another = "➕ Другой шаблон"
tmplt_editing_header = "📝 Редактирование шаблона"
tmplt_err_empty_text = "❌ Текст шаблона не может быть пустым. Пожалуйста, введите текст."
tmplt_deleted_successfully = "✅ Шаблон «{template_text}» успешно удален."

# Настройки приветствия
gr_greetings = "{} Приветствовать новых"
gr_ignore_sys_msgs = "{} Игнор системных сообщений"
gr_edit_message = "✏️ Текст приветствия"
gr_edit_cooldown = "⏱️ Кулдаун: {} дн."

# Настройки ответа на подтверждение заказа
oc_watermark = "{} Водяной знак"
oc_send_reply = "{} Отправлять ответ"
oc_edit_message = "✏️ Текст ответа"

# Настройки вида уведомлений о новых сообщений
mv_incl_my_msg = "{} Мои сообщения"
mv_incl_fp_msg = "{} Сообщения FunPay"
mv_incl_bot_msg = "{} Сообщения бота"
mv_only_my_msg = "{} Только мои"
mv_only_fp_msg = "{} Только от FunPay"
mv_only_bot_msg = "{} Только от бота"
mv_show_image_name = "{} Имена изображений"

# Плагины
pl_add = "➕ Добавить плагин"
pl_activate = "🚀 Активировать"
pl_deactivate = "💤 Деактивировать"
pl_commands = "⌨️ Команды"
pl_settings = "⚙️ Настройки"
pl_status_active = "Статус: Активен 🚀"
pl_status_inactive = "Статус: Неактивен 💤"
pl_no_commands = "У этого плагина нет зарегистрированных команд."
pl_delete_handler_failed = "⚠️ Ошибка при выполнении обработчика удаления плагина «{plugin_name}». Плагин удален из списка, но его данные или файлы могли остаться. Проверьте логи."
pl_deleted_successfully = "✅ Плагин «{plugin_name}» успешно удален. Перезапустите FPCortex, чтобы изменения вступили в силу."
pl_file_delete_error = "⚠️ Не удалось удалить файл плагина «{plugin_path}». Проверьте права доступа и логи."
pl_safe_source = "Источник безопасных плагинов"
pl_channel_button = "Канал FunPay Cortex"


# Конфиги
cfg_download_main = "📥 Основной конфиг"
cfg_download_ar = "📥 Конфиг автоответчика"
cfg_download_ad = "📥 Конфиг автовыдачи"
cfg_upload_main = "📤 Основной конфиг"
cfg_upload_ar = "📤 Конфиг автоответчика"
cfg_upload_ad = "📤 Конфиг автовыдачи"

# Авторизованные пользователи
tg_block_login = "{} Блокировать вход по паролю"

# Прокси
prx_proxy_add = "➕ Добавить прокси"
proxy_status_enabled = "Включены"
proxy_status_disabled = "Выключены"
proxy_check_status_enabled = "Включена"
proxy_check_status_disabled = "Выключена"
proxy_not_used_currently = "не используется"
proxy_not_selected = "не выбран"
proxy_check_interval_info = "Интервал авто-проверки: {interval} мин."
proxy_global_status_header = "Общий статус прокси-модуля"
proxy_module_status_label = "Состояние модуля:"
proxy_health_check_label = "Авто-проверка прокси:"
proxy_current_in_use_label = "Текущий прокси в работе:"
proxy_select_error_not_found = "⚠️ Ошибка: этот прокси больше не существует в списке."
proxy_select_error_invalid_format = "⚠️ Ошибка: выбранный прокси имеет неверный формат."
proxy_selected_and_applied = "✅ Прокси {proxy_str} выбран и применен."
proxy_selected_not_applied = "ℹ️ Прокси {proxy_str} выбран. Включите модуль прокси в настройках, чтобы он начал использоваться."
proxy_deleted_successfully = "✅ Прокси {proxy_str} успешно удален из списка."
proxy_delete_error_not_found = "⚠️ Ошибка: прокси для удаления не найден в списке."

# Объявления
an_an = "{} Объявления"
an_ad = "{} Реклама"

# Новый заказ
ord_refund = "💸 Вернуть средства"
ord_open = "🔗 Страница заказа"
ord_answer = "✉️ Ответить"
ord_templates = "📝 Шаблоны"

# Новое сообщение
msg_reply = "✉️ Ответить"
msg_reply2 = "✉️ Еще раз"
msg_templates = "📝 Шаблоны"
msg_more = "🔎 Подробнее"

# Текста сообщений
access_denied = """Привет, <b><i>{}</i></b>! 👋

К сожалению, у тебя нет доступа. ⛔

🔑 Введи <u><b>секретный пароль</b></u> (указанный при первой настройке), чтобы войти.

✨ <b>FunPay Cortex</b> - твой лучший помощник на FunPay!
📢 Узнать больше и присоединиться к нашему сообществу можно на канале: <a href="https://t.me/FunPayCortex"><b>FunPay Cortex Channel</b></a>"""
access_granted = "Доступ открыт! 🔓\n\n" \
                 "📢 Учти: уведомления в <b><u>этот чат</u></b> пока не приходят.\n\n" \
                 "🔔 Настроить их можно в меню.\n\n" \
                 "⚙️ Открыть меню настроек <i>FPCortex</i>: /menu"
access_granted_notification = "<b>🚨 ВНИМАНИЕ! 🚨\n\n\n</b>" * 3 + "\n\n\n🔐 Пользователь \"<a href=\"tg://user?id={1}\">{0}</a>\" " \
                                                                 "<b>(ID: {1}) получил доступ к панели управления Telegram! 🔓</b>"
param_disabled = "❌ Эта настройка выключена глобально и не может быть изменена для данного лота.\n\n" \
                 "🌍 Глобальные настройки доступны здесь: " \
                 "/menu -> 🔧 Общие настройки."
old_mode_help = """<b>Новый режим получения сообщений</b> 🚀
✅ <i>FPCortex</i> видит всю историю чата и все детали новых сообщений.
✅ <i>FPCortex</i> может видеть изображения и пересылать их в <i>Telegram</i>.
✅ <i>FPCortex</i> точно определяет автора: ты, собеседник или арбитраж.
❌ Чат становится "прочитанным" (не горит оранжевым), так как <i>FPCortex</i> читает всю историю.

<b>Устаревший режим получения сообщений</b> 🐢
✅ Непрочитанные тобой чаты остаются оранжевыми.
✅ Работает немного быстрее.
❌ <i>FPCortex</i> видит только последнее сообщение. Если придет несколько сообщений подряд – увидит только последнее.
❌ <i>FPCortex</i> не видит изображения и не может их переслать.
❌ <i>FPCortex</i> не всегда точно определяет автора. Если чат не прочитан – сообщение от собеседника, иначе – от тебя. Эта логика может давать сбои. Арбитраж также не будет определен.

💡 Если нажать кнопку <code>Подробнее</code> в уведомлении, <i>FPCortex</i> "прочитает" чат, покажет последние 15 сообщений (включая картинки) и сможет точно определить автора."""
bot_started = """✅ Telegram-бот запущен!
Ты можешь <b><u>настраивать конфиги</u></b> и <b><u>использовать все функции <i>Telegram</i>-бота</u></b>.

⏳ <i>FPCortex</i> <b><u>пока не инициализирован</u></b>, его функции неактивны.
Когда <i>FPCortex</i> запустится, это сообщение изменится.

🕒 Если инициализация занимает много времени, проверь логи командой /logs."""
fpc_init = """✅ <b><u>FPCortex инициализирован!</u></b>
ℹ️ <b><i>Версия:</i></b> <code>{}</code>
👑 <b><i>Аккаунт:</i></b>  <code>{}</code> | <code>{}</code>
💰 <b><i>Баланс:</i></b> <code>{}₽, {}$, {}€</code>
📊 <b><i>Активные заказы:</i></b>  <code>{}</code>

👨‍💻 <b><i>Автор:</i></b> @beedge"""

create_test_ad_key = "Введи название лота для теста автовыдачи."
test_ad_key_created = """✅ Создан одноразовый ключ для выдачи лота «<code>{}</code>».
Отправь команду ниже в чат с покупателем, чтобы выдать товар:
<code>!автовыдача {}</code>"""
about = """<b>🧠 FPCortex 🧠 v{}</b>
<i>Автор:</i> @beedge"""
sys_info = """<b>📊 Системная сводка</b>

<b>⚙️ CPU:</b>
{}
    Используется <i>FPCortex</i>: <code>{}%</code>

<b>💾 RAM:</b>
    Всего:  <code>{} MB</code>
    Использовано:  <code>{} MB</code>
    Свободно:  <code>{} MB</code>
    Используется ботом:  <code>{} MB</code>

<b>⏱️ Прочее:</b>
    Аптайм:  <code>{}</code>
    ID чата:  <code>{}</code>"""
act_blacklist = """Введи никнейм пользователя для добавления в черный список."""
already_blacklisted = "❌ Пользователь <code>{}</code> уже в черном списке."
user_blacklisted = "✅ Пользователь <code>{}</code> добавлен в черный список."
act_unban = "Введи никнейм пользователя для удаления из черного списка."
not_blacklisted = "❌ Пользователя <code>{}</code> нет в черном списке."
user_unbanned = "✅ Пользователь <code>{}</code> удален из черного списка."
blacklist_empty = "🚫 Черный список пуст."
act_proxy = "Введи прокси в формате <u>login:password@ip:port</u> или <u>ip:port</u>."
proxy_already_exists = "❌ Прокси <code>{}</code> уже добавлен."
proxy_added = "✅ Прокси <u>{}</u> успешно добавлен."
proxy_format = "❌ Неверный формат прокси. Нужен: <u>login:password@ip:port</u> или <u>ip:port</u>."
proxy_adding_error = "⚠️ Ошибка при добавлении прокси."
proxy_undeletable = "❌ Этот прокси используется и не может быть удален."
act_edit_watermark = "Введи новый текст водяного знака. Примеры:\n{}\n<code>𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙</code>\n" \
                     "<code>FPCortex</code>\n<code>[FunPay / Cortex]</code>\n<code>𝑭𝑷𝑪𝒙</code>\n" \
                     "<code>FPCx</code>\n<code>🤖</code>\n<code>🧠</code>\n\n" \
                     "Примеры можно скопировать и отредактировать.\nУчти, что на FunPay эмодзи " \
                     "🧠 может выглядеть иначе.\n\nЧтобы удалить водяной знак, отправь <code>-</code>."
v_edit_watermark_current = "Текущий" # Новый ключ
watermark_changed = "✅ Водяной знак изменен."
watermark_deleted = "✅ Водяной знак удален."
watermark_error = "⚠️ Некорректный водяной знак."
logfile_not_found = "❌ Лог-файл не найден."
logfile_sending = "Отправляю лог-файл (это может занять время)... ⏳"
logfile_error = "⚠️ Не удалось отправить лог-файл."
logfile_deleted = "🗑️ Удалено {} лог-файлов."
update_no_tags = "❌ Не удалось получить список версий с GitHub. Попробуйте позже."
update_lasted = "✅ У вас установлена последняя версия FPCortex {}."
update_get_error = "❌ Не удалось получить информацию о новой версии с GitHub. Попробуйте позже."
update_available = "✨ <b>Доступна новая версия FPCortex!</b> ✨\n\n{}"
update_update = "Чтобы обновиться, введите команду /update"
update_backup = "✅ Создана резервная копия (конфиги, хранилище, плагины): <code>backup.zip</code>.\n\n" \
                "🔒 <b>ВАЖНО:</b> НЕ ОТПРАВЛЯЙТЕ этот архив НИКОМУ. Он содержит все данные и настройки бота (включая golden_key и товары)."
update_backup_error = "⚠️ Не удалось создать резервную копию."
update_backup_not_found = "❌ Резервная копия не найдена."
update_downloaded = "✅ Загружено обновление {}. Пропущено {} элементов (если это были старые релизы). Устанавливаю..."
update_download_error = "⚠️ Ошибка при загрузке архива обновления."
update_done = "✅ Обновление установлено! Перезапустите <i>FPCortex</i> командой /restart"
update_done_exe = "✅ Обновление установлено! Новый <code>FPCortex.exe</code> находится в папке <code>update</code>. " \
                  "Выключите <i>FPCortex</i>, замените старый <code>FPCortex.exe</code> новым " \
                  "и запустите <code>Start.bat</code>."
update_install_error = "⚠️ Ошибка при установке обновления."

restarting = "Перезапускаюсь... 🚀"
power_off_0 = """<b>Вы уверены, что хотите меня выключить?</b> 🤔
Включить обратно через <i>Telegram</i> <b><u>не получится!</u></b>"""
power_off_1 = "Еще раз, на всякий случай... <b><u>Точно выключаем?</u></b> 😟"
power_off_2 = """Просто чтобы ты знал:
придется заходить на сервер/компьютер и запускать меня вручную! 💻"""
power_off_3 = """Не настаиваю, но если нужно применить изменения основного конфига,
можно просто перезапустить меня командой /restart. 😉"""
power_off_4 = "Ты вообще читаешь мои сообщения? 😉 Давай проверим: да = нет, нет = да. " \
              "Уверен, ты даже не читаешь, а я тут важную информацию пишу."
power_off_5 = "Итак, твой окончательный ответ... да? 😏"
power_off_6 = "Хорошо, хорошо, выключаюсь... 💤"
power_off_cancelled = "Выключение отменено. Продолжаем работу! 👍"
power_off_error = "❌ Эта кнопка больше неактуальна. Вызови меню выключения снова."
enter_msg_text = "Введи текст сообщения:"
msg_sent = "✅ Сообщение отправлено в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sent_short = "✅ Сообщение отправлено."
msg_sending_error = "⚠️ Не удалось отправить сообщение в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sending_error_short = "⚠️ Не удалось отправить сообщение."
send_img = "Отправь мне изображение 🖼️"
greeting_changed = "✅ Текст приветствия изменен."
greeting_cooldown_changed = "✅ Кулдаун приветствия изменен: {} дн."
order_confirm_changed = "✅ Текст ответа на подтверждение заказа изменен!"
review_reply_changed = "✅ Текст ответа на {}⭐ отзыв изменен!"
review_reply_empty = "⚠️ Ответ на {}⭐ отзыв не задан."
review_reply_text = "Ответ на {}⭐ отзыв:\n<code>{}</code>"
get_chat_error = "⚠️ Не удалось получить данные чата."
viewing = "Смотрит"
you = "Ты"
support = "тех. поддержка"
photo = "Фото"
refund_attempt = "⚠️ Не удалось вернуть средства по заказу <code>#{}</code>. Осталось попыток: <code>{}</code>."
refund_error = "❌ Не удалось вернуть средства по заказу <code>#{}</code>."
refund_complete = "✅ Средства по заказу <code>#{}</code> возвращены."
updating_profile = "Обновляю статистику аккаунта... 📊"
profile_updating_error = "⚠️ Не удалось обновить статистику."
acc_balance_available = "доступно"
act_change_golden_key = "🔑 Введи свой golden_key:"
cookie_changed = "✅ golden_key успешно изменен{}.\n"
cookie_changed2 = "Перезапусти бота командой /restart, чтобы применить изменения."
cookie_incorrect_format = "❌ Неверный формат golden_key. Попробуй еще раз."
cookie_error = "⚠️ Не удалось авторизоваться. Возможно, введен неверный golden_key?"
ad_lot_not_found_err = "⚠️ Лот с индексом <code>{}</code> не найден."
ad_already_ad_err = "⚠️ У лота <code>{}</code> уже настроена автовыдача."
ad_lot_already_exists = "⚠️ К лоту <code>{}</code> уже привязана автовыдача."
ad_lot_linked = "✅ Автовыдача привязана к лоту <code>{}</code>."
ad_link_gf = "Введи название файла с товарами.\nЧтобы отвязать файл, отправь <code>-</code>\n\n" \
             "Если файла нет, он будет создан автоматически."
ad_gf_unlinked = "✅ Файл товаров отвязан от лота <code>{}</code>."
ad_gf_linked = "✅ Файл <code>storage/products/{}</code> привязан к лоту <code>{}</code>."
ad_gf_created_and_linked = "✅ Файл <code>storage/products/{}</code> <b><u>создан</u></b> и привязан к лоту <code>{}</code>."
ad_creating_gf = "⏳ Создаю файл <code>storage/products/{}</code>..."
ad_product_var_err = "⚠️ К лоту <code>{}</code> привязан файл товаров, но в тексте выдачи нет переменной <code>$product</code>."
ad_product_var_err2 = "⚠️ Нельзя привязать файл: в тексте выдачи нет переменной <code>$product</code>."
ad_text_changed = "✅ Текст выдачи для лота <code>{}</code> изменен на:\n<code>{}</code>"
ad_updating_lots_list = "Обновляю данные о лотах и категориях... ⏳"
ad_lots_list_updating_err = "⚠️ Не удалось обновить данные о лотах и категориях."
gf_not_found_err = "⚠️ Файл товаров с индексом <code>{}</code> не найден."
copy_lot_name = "Отправь точное название лота (как на FunPay)."
act_create_gf = "Введи название для нового файла товаров (например, 'ключи_стим')."
gf_name_invalid = "🚫 Недопустимое имя файла.\n\n" \
                  "Разрешены только <b><u>английские</u></b> " \
                  "и <b><u>русские</u></b> буквы, цифры, а также символы <code>_</code>, <code>-</code> и <code>пробел</code>."
gf_already_exists_err = "⚠️ Файл <code>{}</code> уже существует."
gf_creation_err = "⚠️ Ошибка при создании файла <code>{}</code>."
gf_created = "✅ Файл <code>storage/products/{}</code> создан."
gf_amount = "Товаров в файле"
gf_uses = "Используется в лотах"
gf_send_new_goods = "Отправь товары для добавления. Каждый товар с новой строки (<code>Shift+Enter</code>)."
gf_add_goods_err = "⚠️ Не удалось добавить товары в файл."
gf_new_goods = "✅ Добавлено <code>{}</code> товар(а/ов) в файл <code>storage/products/{}</code>."
gf_empty_error = "📂 Файл storage/products/{} пуст."
gf_linked_err = "⚠️ Файл <code>storage/products/{}</code> привязан к одному или нескольким лотам.\n" \
                "Сначала отвяжи его от всех лотов, потом удаляй."
gf_deleting_err = "⚠️ Не удалось удалить файл <code>storage/products/{}</code>."
ar_cmd_not_found_err = "⚠️ Команда с индексом <code>{}</code> не найдена."
ar_subcmd_duplicate_err = "⚠️ Команда <code>{}</code> дублируется в наборе."
ar_cmd_already_exists_err = "⚠️ Команда <code>{}</code> уже существует."
ar_enter_new_cmd = "Введи новую команду (или несколько, разделяя их символом <code>|</code>)."
ar_cmd_added = "✅ Новая команда <code>{}</code> добавлена."
ar_response_text = "Текст ответа"
ar_notification_text = "Текст уведомления"
ar_response_text_changed = "✅ Текст ответа для команды <code>{}</code> изменен на:\n<code>{}</code>"
ar_notification_text_changed = "✅ Текст уведомления для команды <code>{}</code> изменен на:\n<code>{}</code>"
cfg_main = "Основной конфиг. 🔒 ВАЖНО: НЕ ОТПРАВЛЯЙ этот файл НИКОМУ."
cfg_ar = "Конфиг автоответчика."
cfg_ad = "Конфиг автовыдачи."
cfg_not_found_err = "⚠️ Конфиг {} не найден."
cfg_empty_err = "📂 Конфиг {} пуст."
tmplt_not_found_err = "⚠️ Шаблон с индексом <code>{}</code> не найден."
tmplt_already_exists_err = "⚠️ Такой шаблон уже существует."
tmplt_added = "✅ Шаблон добавлен."
tmplt_msg_sent = "✅ Сообщение по шаблону отправлено в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>:\n\n<code>{}</code>"
pl_not_found_err = "⚠️ Плагин с UUID <code>{}</code> не найден."
pl_file_not_found_err = "⚠️ Файл <code>{}</code> не найден.\nПерезапусти <i>FPCortex</i> командой /restart."
pl_commands_list = "Команды плагина <b><i>{}</i></b>:"
pl_author = "Автор"
pl_new = "Отправь мне файл плагина (.py).\n\n<b>☢️ ВНИМАНИЕ!</b> Загрузка плагинов из непроверенных источников может быть опасна."
au_user_settings = "Настройки для пользователя {}"
adv_fpc = "😎 FPCortex - твой лучший ассистент для FunPay!"
adv_description = """🧠 FPCortex v{} 🚀

🤖 Автовыдача товаров
📈 Авто-буст лотов
💬 Умный автоответчик
♻️ Автовідновлення лотів
📦 Автодеактивация (если товары закончились)
🔝 Всегда онлайн
📲 Telegram-уведомления
🕹️ Полный контроль через Telegram
🧩 Поддержка плагинов
🌟 И многое другое!

👨‍💻 Автор: @beedge"""

# - Описания меню
desc_main = "Привет! Выбери, что настроим 👇"
desc_lang = "Выбери язык интерфейса:"
desc_gs = "Здесь можно включать и выключать основные функции <i>FPCortex</i>."
desc_ns = """Настрой уведомления для этого чата.
Каждый чат настраивается отдельно!

ID этого чата: <code>{}</code>"""
desc_bl = "Установи ограничения для пользователей из черного списка."
desc_ar = "Добавь команды для автоответчика или отредактируй существующие."
desc_ar_list = "Выбери команду или набор команд для редактирования:"
desc_ad = "Настройки автовыдачи: привязка к лотам, управление файлами товаров и т.д."
desc_ad_list = "Список лотов с настроенной автовыдачей. Выбери лот для редактирования:"
desc_ad_fp_lot_list = "Список лотов из твоего профиля FunPay. Выбери лот, чтобы настроить автовыдачу.\n" \
                      "Если нужного лота нет, нажми <code>🔄 Обновить</code>.\n\n" \
                      "Последнее сканирование: {}"
desc_gf = "Выбери файл товаров для управления:"
desc_mv = "Настрой, как будут выглядеть уведомления о новых сообщениях."
desc_gr = "Настрой приветственные сообщения для новых диалогов.\n\n<b>Текущий текст приветствия:</b>\n<code>{}</code>"
desc_oc = "Настрой сообщение, которое будет отправляться при подтверждении заказа.\n\n<b>Текущий текст сообщения:</b>\n<code>{}</code>"
desc_or = "Настрой автоматические ответы на отзывы."
desc_an = "Настройки уведомлений об объявлениях."
desc_cfg = "Здесь можно скачать или загрузить файлы конфигурации."
desc_tmplt = "Управляй шаблонами быстрых ответов."
desc_pl = "Информация и настройки плагинов.\n\n" \
          "⚠️ <b>ВАЖНО:</b> После активации, деактивации, добавления или удаления плагина, " \
          "<b><u>необходимо перезапустить бота</u></b> командой /restart!"
desc_au = "Настройки авторизации пользователей в панели управления Telegram."
desc_proxy = "Управление прокси-серверами для работы бота."
unknown_action = "Неизвестное действие или кнопка устарела." # Новый ключ

# - Описание команд
cmd_menu = "открыть главное меню"
cmd_language = "сменить язык интерфейса"
cmd_profile = "посмотреть статистику аккаунта"
cmd_golden_key = "изменить golden_key (токен доступа)"
cmd_test_lot = "создать тестовый ключ автовыдачи"
cmd_upload_chat_img = "(чат) загрузить картинку на FunPay"
cmd_upload_offer_img = "(лот) загрузить картинку на FunPay"
cmd_upload_plugin = "загрузить новый плагин"
cmd_ban = "добавить пользователя в ЧС"
cmd_unban = "удалить пользователя из ЧС"
cmd_black_list = "показать черный список"
cmd_watermark = "изменить водяной знак сообщений"
cmd_logs = "скачать текущий лог-файл"
cmd_del_logs = "удалить старые лог-файлы"
cmd_about = "информация о боте"
cmd_check_updates = "проверить обновления"
cmd_update = "обновить бота"
cmd_sys = "системная информация и нагрузка"
cmd_create_backup = "создать резервную копию"
cmd_get_backup = "скачать резервную копию"
cmd_restart = "перезапустить FPCortex"
cmd_power_off = "выключить FPCortex"

# - Описание переменных
v_edit_greeting_text = "Введи текст приветственного сообщения:"
v_edit_greeting_cooldown = "Введи кулдаун для приветствия (в днях, например, 0.5 для 12 часов):"
v_edit_order_confirm_text = "Введи текст ответа на подтверждение заказа:"
v_edit_review_reply_text = "Введи текст ответа на отзыв с {}⭐:"
v_edit_delivery_text = "Введи новый текст для автовыдачи товара:"
v_edit_response_text = "Введи новый текст ответа для команды:"
v_edit_notification_text = "Введи новый текст для Telegram-уведомления:"
V_new_template = "Введи текст нового шаблона ответа:"
v_list = "Доступные переменные:"
v_date = "<code>$date</code> - дата (ДД.ММ.ГГГГ)"
v_date_text = "<code>$date_text</code> - дата (1 января)"
v_full_date_text = "<code>$full_date_text</code> - дата (1 января 2001 года)"
v_time = "<code>$time</code> - время (ЧЧ:ММ)"
v_full_time = "<code>$full_time</code> - время (ЧЧ:ММ:СС)"
v_photo = "<code>$photo=[ID_ФОТО]</code> - картинка (ID через /upload_chat_img)"
v_sleep = "<code>$sleep=[СЕКУНДЫ]</code> - задержка перед отправкой (например, $sleep=2)"
v_order_id = "<code>$order_id</code> - ID заказа (без #)"
v_order_link = "<code>$order_link</code> - ссылка на заказ"
v_order_title = "<code>$order_title</code> - название заказа"
v_order_params = "<code>$order_params</code> - параметры заказа"
v_order_desc_and_params = "<code>$order_desc_and_params</code> - название и/или параметры заказа"
v_order_desc_or_params = "<code>$order_desc_or_params</code> - название или параметры заказа"
v_game = "<code>$game</code> - название игры"
v_category = "<code>$category</code> - название подкатегории"
v_category_fullname = "<code>$category_fullname</code> - полное название (подкатегория + игра)"
v_product = "<code>$product</code> - товар из файла (если не привязан, не заменится)"
v_chat_id = "<code>$chat_id</code> - ID чата"
v_chat_name = "<code>$chat_name</code> - название чата"
v_message_text = "<code>$message_text</code> - текст сообщения собеседника"
v_username = "<code>$username</code> - никнейм собеседника"
v_cpu_core = "Ядро" # Новый ключ

# Текста исключений
exc_param_not_found = "Параметр \"{}\" не найден."
exc_param_cant_be_empty = "Значение параметра \"{}\" не может быть пустым."
exc_param_value_invalid = "Недопустимое значение для \"{}\". Разрешено: {}. Текущее: \"{}\"."
exc_goods_file_not_found = "Файл товаров \"{}\" не найден."
exc_goods_file_is_empty = "Файл \"{}\" пуст."
exc_not_enough_items = "В файле \"{}\" не хватает товаров. Нужно: {}, доступно: {}."
exc_no_product_var = "Указан \"productsFileName\", но в параметре \"response\" нет переменной $product."
exc_no_section = "Секция отсутствует."
exc_section_duplicate = "Обнаружен дубликат секции."
exc_cmd_duplicate = "Команда или суб-команда \"{}\" уже существует."
exc_cfg_parse_err = "Ошибка в конфиге {}, секция [{}]: {}"
exc_plugin_field_not_found = "Не удалось загрузить плагин \"{}\": отсутствует обязательное поле \"{}\"."

# Логи
log_tg_initialized = "$MAGENTATelegram бот инициализирован."
log_tg_started = "$CYANTelegram бот $YELLOW@{}$CYAN запущен."
log_tg_handler_error = "Произошла ошибка при выполнении хэндлера Telegram бота."
log_tg_update_error = "Произошла ошибка ({}) при получении обновлений Telegram (введен некорректный токен?)."
log_tg_notification_error = "Произошла ошибка при отправке уведомления в чат $YELLOW{}$RESET."
log_access_attempt = "$MAGENTA@{} (ID: {})$RESET попытался получить доступ к ПУ. Сдерживаю его как могу!"
log_click_attempt = "$MAGENTA@{} (ID: {})$RESET нажимает кнопки ПУ в чате $MAGENTA@{} (ID: {})$RESET. У него ничего не выйдет!"
log_access_granted = "$MAGENTA@{} (ID: {})$RESET получил доступ к ПУ."
log_new_ad_key = "$MAGENTA@{} (ID: {})$RESET создал ключ для выдачи $YELLOW{}$RESET: $CYAN{}$RESET."
log_user_blacklisted = "$MAGENTA@{} (ID: {})$RESET добавил $YELLOW{}$RESET в ЧС."
log_user_unbanned = "$MAGENTA@{} (ID: {})$RESET удалил $YELLOW{}$RESET из ЧС."
log_watermark_changed = "$MAGENTA@{} (ID: {})$RESET изменил водяной знак сообщений на $YELLOW{}$RESET."
log_watermark_deleted = "$MAGENTA@{} (ID: {})$RESET удалил водяной знак сообщений."
log_greeting_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст приветствия на $YELLOW{}$RESET."
log_greeting_cooldown_changed = "$MAGENTA@{} (ID: {})$RESET изменил кулдаун приветсвенного сообщения на $YELLOW{}$RESET дн."
log_order_confirm_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст ответа на подтверждение заказа на $YELLOW{}$RESET."
log_review_reply_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст ответа на отзыв с {} зв. на $YELLOW{}$RESET."
log_param_changed = "$MAGENTA@{} (ID: {})$RESET изменил параметр $CYAN{}$RESET секции $YELLOW[{}]$RESET на $YELLOW{}$RESET."
log_notification_switched = "$MAGENTA@{} (ID: {})$RESET переключил уведомления $YELLOW{}$RESET для чата $YELLOW{}$RESET на $CYAN{}$RESET."
log_ad_linked = "$MAGENTA@{} (ID: {})$RESET привязал авто-выдачу к лоту $YELLOW{}$RESET."
log_ad_text_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст выдачи лота $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ad_deleted = "$MAGENTA@{} (ID: {})$RESET удалил авто-выдачу лота $YELLOW{}$RESET."
log_gf_created = "$MAGENTA@{} (ID: {})$RESET создал товарный файл $YELLOWstorage/products/{}$RESET."
log_gf_unlinked = "$MAGENTA@{} (ID: {})$RESET отвязал товарный файл от лота $YELLOW{}$RESET."
log_gf_linked = "$MAGENTA@{} (ID: {})$RESET привязал товарный файл $YELLOWstorage/products/{}$RESET к лоту $YELLOW{}$RESET."
log_gf_created_and_linked = "$MAGENTA@{} (ID: {})$RESET создал и привязал товарный файл $YELLOWstorage/products/{}$RESET к лоту $YELLOW{}$RESET."
log_gf_new_goods = "$MAGENTA@{} (ID: {})$RESET добавил $CYAN{}$RESET товар(-а, -oв) в файл $YELLOWstorage/products/{}$RESET."
log_gf_downloaded = "$MAGENTA@{} (ID: {})$RESET запросил товарный файл $YELLOWstorage/products/{}$RESET."
log_gf_deleted = "$MAGENTA@{} (ID: {})$RESET удалил товарный файл $YELLOWstorage/products/{}$RESET."
log_ar_added = "$MAGENTA@{} (ID: {})$RESET добавил новую команду $YELLOW{}$RESET."
log_ar_response_text_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст ответа команды $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ar_notification_text_changed = "$MAGENTA@{} (ID: {})$RESET изменил текст уведомления команды $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ar_cmd_deleted = "$MAGENTA@{} (ID: {})$RESET удалил команду $YELLOW{}$RESET."
log_cfg_downloaded = "$MAGENTA@{} (ID: {})$RESET запросил конфиг $YELLOW{}$RESET."
log_tmplt_added = "$MAGENTA@{} (ID: {})$RESET добавил заготовку ответа $YELLOW\"{}\"$RESET."
log_tmplt_deleted = "$MAGENTA@{} (ID: {})$RESET удалил заготовку ответа $YELLOW\"{}\"$RESET."
log_pl_activated = "$MAGENTA@{} (ID: {})$RESET активировал плагин $YELLOW\"{}\"$RESET."
log_pl_deactivated = "$MAGENTA@{} (ID: {})$RESET деактивировал плагин $YELLOW\"{}\"$RESET."
log_pl_deleted = "$MAGENTA@{} (ID: {})$RESET удалил плагин $YELLOW\"{}\"$RESET."
log_pl_delete_handler_err = "Произошла ошибка при выполнении хендлера удаления плагина $YELLOW\"{}\"$RESET."

# Логи хэндлеров
log_new_msg = "$MAGENTA┌──$RESET Новое сообщение в переписке с пользователем $YELLOW{} (CID: {}):"
log_sending_greetings = "Пользователь $YELLOW{} (CID: {})$RESET написал впервые! Отправляю приветственное сообщение..."
log_new_cmd = "Получена команда $YELLOW{}$RESET в чате с пользователем $YELLOW{} (CID: {})$RESET."
ntfc_new_order = "💰 <b>Новый заказ:</b> <code>{}</code>\n\n<b><i>🙍‍♂️ Покупатель:</i></b>  <code>{}</code>\n" \
                 "<b><i>💵 Сумма:</i></b>  <code>{}</code>\n<b><i>📇 ID:</i></b> <code>#{}</code>\n\n<i>{}</i>"
ntfc_new_order_not_in_cfg = "ℹ️ Товар не будет выдан, т.к. к лоту не привязана авто-выдача."
ntfc_new_order_ad_disabled = "ℹ️ Товар не будет выдан, т.к. авто-выдача отключена в глобальных переключателях."
ntfc_new_order_ad_disabled_for_lot = "ℹ️ Товар не будет выдан, т.к. авто-выдача отключена для данного лота."
ntfc_new_order_user_blocked = "ℹ️ Товар не будет выдан, т.к. пользователь находится в ЧС и включена блокировка авто-выдачи."
ntfc_new_order_will_be_delivered = "ℹ️ Товар будет выдан в ближайшее время."
ntfc_new_review = "🔮 Вы получили {} за заказ <code>{}</code>!\n\n💬<b>Отзыв:</b>\n<code>{}</code>{}"
ntfc_review_reply_text = "\n\n🗨️<b>Ответ:</b> \n<code>{}</code>"

# Логи кортекса
crd_proxy_detected = "Обнаружен прокси."
crd_checking_proxy = "Выполняю проверку прокси..."
crd_proxy_err = "Не удалось подключиться к прокси. Убедитесь, что данные введены верно."
crd_proxy_success = "Прокси успешно проверен! IP-адрес: $YELLOW{}$RESET."
crd_acc_get_timeout_err = "Не удалось загрузить данные об аккаунте: превышен тайм-аут ожидания."
crd_acc_get_unexpected_err = "Произошла непредвиденная ошибка при получении данных аккаунта."
crd_try_again_in_n_secs = "Повторю попытку через {} секунд(-у/-ы)..."
crd_getting_profile_data = "Получаю данные о лотах и категориях..."
crd_profile_get_timeout_err = "Не удалось загрузить данные о лотах аккаунта: превышен тайм-аут ожидания."
crd_profile_get_unexpected_err = "Произошла непредвиденная ошибка при получении данных о лотах и категориях."
crd_profile_get_too_many_attempts_err = "Произошло ошибка при получении данных о лотах и категориях: превышено кол-во попыток ({})."
crd_profile_updated = "Обновил информацию о лотах $YELLOW({})$RESET и категориях $YELLOW({})$RESET профиля."
crd_tg_profile_updated = "Обновил информацию о лотах $YELLOW({})$RESET и категориях $YELLOW({})$RESET профиля (TG ПУ)."
crd_raise_time_err = 'Не удалось поднять лоты категории $CYAN\"{}\"$RESET. FunPay говорит: "{}". Следующая попытка через {}.'
crd_raise_unexpected_err = "Произошла непредвиденная ошибка при попытке поднять лоты категории $CYAN\"{}\"$RESET. Пауза на 10 секунд..."
crd_raise_status_code_err = "Ошибка {} при поднятии лотов категории $CYAN\"{}\"$RESET. Пауза на 1 мин..."
crd_lots_raised = "Все лоты категории $CYAN\"{}\"$RESET подняты!"
crd_raise_wait_3600 = "Следующая попытка через {}."
crd_msg_send_err = "Произошла ошибка при отправке сообщения в чат $YELLOW{}$RESET."
crd_msg_attempts_left = "Осталось попыток: $YELLOW{}$RESET."
crd_msg_no_more_attempts_err = "Не удалось отправить сообщение в чат $YELLOW{}$RESET: превышено кол-во попыток."
crd_msg_sent = "Отправил сообщение в чат $YELLOW{}."
crd_session_timeout_err = "Не удалось обновить сессию: превышен тайм-аут ожидания."
crd_session_unexpected_err = "Произошла непредвиденная ошибка при обновлении сессии."
crd_session_no_more_attempts_err = "Не удалось обновить сессию: превышено кол-во попыток."
crd_session_updated = "Сессия обновлена."
crd_raise_loop_started = "$CYANЦикл автоподнятия лотов запущен (это не значит, что автоподнятие лотов включено)."
crd_raise_loop_not_started = "$CYANЦикл автоподнятия не был запущен, т.к. на аккаунте не обнаружен лотов."
crd_session_loop_started = "$CYANЦикл обновления сессии запущен."
crd_no_plugins_folder = "Папка с плагинами не обнаружена."
crd_no_plugins = "Плагины не обнаружены."
crd_plugin_load_err = "Не удалось загрузить плагин {}."
crd_invalid_uuid = "Не удалось загрузить плагин {}: невалидный UUID."
crd_uuid_already_registered = "UUID {} ({}) уже зарегистрирован."
crd_handlers_registered = "Хэндлеры из $YELLOW{}.py$RESET зарегистрированы."
crd_handler_err = "Произошла ошибка при выполнении хэндлера."
crd_tg_au_err = "Не удалось изменить сообщение с информацией о пользователе: {}. Попробую без ссылки."

acc_balance_available = "доступно"
gf_infinity = "бесконечно"
gf_count_error = "ошибка подсчета"
gf_file_not_found_short = "не найден"
gf_not_linked = "не привязан"
gf_file_created_now = "создан"
gf_file_creation_error_short = "ошибка создания"
no_lots_using_file = "Ни один лот не использует этот файл."
gf_no_products_to_add = "Не было введено товаров для добавления."
gf_deleted_successfully = "Файл «{file_name}» успешно удален."
gf_already_deleted = "Файл «{file_name}» уже был удален."
ar_no_valid_commands_entered = "Не введено ни одной корректной команды."
ar_default_response_text = "Ответ для этой команды еще не настроен. Отредактируйте его."
ar_default_notification_text = "Пользователь $username ввел команду: $message_text"
ar_command_deleted_successfully = "Команда/сет «{command_name}» успешно удалена."
file_err_not_detected = "❌ Файл не найден в сообщении."
file_err_must_be_text = "❌ Файл должен быть текстовым (например, .txt, .cfg, .py, .json, .ini, .log)."
file_err_wrong_format = "❌ Неверный формат файла: <b><u>.{actual_ext}</u></b> (ожидался <b><u>.{expected_ext}</u></b>)."
file_err_too_large = "❌ Размер файла не должен превышать 20МБ."
file_info_downloading = "⏬ Загружаю файл с серверов Telegram..."
file_err_download_failed = "❌ Произошла ошибка при загрузке файла на сервер бота."
file_info_checking_validity = "🤔 Проверяю содержимое файла..."
file_err_processing_generic = "⚠️ Произошла ошибка при обработке файла: <code>{error_message}</code>"
file_err_utf8_decode = "Произошла ошибка при чтении файла (UTF-8). Убедитесь, что кодировка файла — UTF-8, а формат конца строк — LF."
file_info_main_cfg_loaded = "✅ Основной конфиг успешно загружен.\n\n⚠️ <b>Необходимо перезапустить бота (/restart)</b>, чтобы изменения вступили в силу.\n\nЛюбые изменения основного конфига через переключатели в панели управления до перезапуска отменят загруженные настройки."
file_info_ar_cfg_applied = "✅ Конфиг автоответчика успешно загружен и применен."
file_info_ad_cfg_applied = "✅ Конфиг автовыдачи успешно загружен и применен."
plugin_uploaded_success = "✅ Плагин <code>{filename}</code> успешно загружен.\n\n⚠️Чтобы плагин заработал, <b><u>перезагрузите FPCortex!</u></b> (/restart)"
image_upload_unsupported_format = "❌ Неподдерживаемый формат изображения. Доступны: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>."
image_upload_error_generic = "⚠️ Не удалось выгрузить изображение на FunPay. Подробности смотрите в лог-файле (<code>logs/log.log</code>)."
image_upload_chat_success_info = "Используйте этот ID в текстах автовыдачи или автоответа с переменной <code>$photo</code>.\n\nНапример: <code>$photo={image_id}</code>"
image_upload_offer_success_info = "Используйте этот ID для добавления изображений к вашим лотам на FunPay."
image_upload_success_header = "✅ Изображение успешно выгружено на сервер FunPay.\n\n<b>ID изображения:</b> <code>{image_id}</code>\n\n"
products_file_provide_prompt = "📎 Отправьте мне файл с товарами (.txt):"
products_file_upload_success = "✅ Файл с товарами <code>{filepath}</code> успешно загружен. Товаров в файле: <code>{count}</code>."
products_file_count_error = "⚠️ Произошла ошибка при подсчете товаров в загруженном файле."
main_config_provide_prompt = "⚙️ Отправьте мне файл основного конфига (<code>_main.cfg</code>):"
ar_config_provide_prompt = "🤖 Отправьте мне файл конфига автоответчика (<code>auto_response.cfg</code>):"
ad_config_provide_prompt = "📦 Отправьте мне файл конфига автовыдачи (<code>auto_delivery.cfg</code>):"
pl_status_active = "Статус: Активен 🚀"
pl_status_inactive = "Статус: Неактивен 💤"
pl_no_commands = "У этого плагина нет зарегистрированных команд."
pl_delete_handler_failed = "⚠️ Ошибка при выполнении обработчика удаления плагина «{plugin_name}». Плагин удален из списка, но его данные или файлы могли остаться. Проверьте логи."
pl_deleted_successfully = "✅ Плагин «{plugin_name}» успешно удален. Перезапустите FPCortex, чтобы изменения вступили в силу."
pl_file_delete_error = "⚠️ Не удалось удалить файл плагина «{plugin_path}». Проверьте права доступа и логи."
proxy_status_enabled = "Включены"
proxy_status_disabled = "Выключены"
proxy_check_status_enabled = "Включена"
proxy_check_status_disabled = "Выключена"
proxy_not_used_currently = "не используется"
proxy_not_selected = "не выбран"
proxy_check_interval_info = "Интервал авто-проверки: {interval} мин."
proxy_global_status_header = "Общий статус прокси-модуля"
proxy_module_status_label = "Состояние модуля:"
proxy_health_check_label = "Авто-проверка прокси:"
proxy_current_in_use_label = "Текущий прокси в работе:"
proxy_select_error_not_found = "⚠️ Ошибка: этот прокси больше не существует в списке."
proxy_select_error_invalid_format = "⚠️ Ошибка: выбранный прокси имеет неверный формат."
proxy_selected_and_applied = "✅ Прокси {proxy_str} выбран и применен."
proxy_selected_not_applied = "ℹ️ Прокси {proxy_str} выбран. Включите модуль прокси в настройках, чтобы он начал использоваться."
proxy_deleted_successfully = "✅ Прокси {proxy_str} успешно удален из списка."
proxy_delete_error_not_found = "⚠️ Ошибка: прокси для удаления не найден в списке."
tmplt_editing_header = "📝 Редактирование шаблона"
tmplt_err_empty_text = "❌ Текст шаблона не может быть пустым. Пожалуйста, введите текст."
tmplt_deleted_successfully = "✅ Шаблон «{template_text}» успешно удален."
no_messages_to_display = "Нет сообщений для отображения"
# END OF FILE FunPayCortex/locales/ru.py