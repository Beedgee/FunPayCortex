# START OF FILE FunPayCortex-main/first_setup.py

"""
В данном модуле написана подпрограмма первичной настройки FunPayCortex.
"""

import os
from configparser import ConfigParser
import time
import telebot
from colorama import Fore, Style
from Utils.cortex_tools import validate_proxy, hash_password

default_config = {
    "FunPayAccounts": {
        "Default": ""
    },
    "FunPayAccount_Default": {
        "golden_key": "",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "enabled": "1"
    },
    "FunPay": {
        "autoRaise": "0",
        "autoResponse": "0",
        "autoDelivery": "0",
        "multiDelivery": "0",
        "autoRestore": "0",
        "autoDisable": "0",
        "oldMsgGetMode": "0",
        "keepSentMessagesUnread": "0",
        "locale": "ru"
    },
    "Telegram": {
        "enabled": "0",
        "token": "",
        "secretKeyHash": "УстановитеСвойПароль",
        "blockLogin": "0"
    },
    "Manager": {
        "registration_key": ""
    },
    "BlockList": {
        "blockDelivery": "0",
        "blockResponse": "0",
        "blockNewMessageNotification": "0",
        "blockNewOrderNotification": "0",
        "blockCommandNotification": "0"
    },
    "NewMessageView": {
        "includeMyMessages": "1",
        "includeFPMessages": "1",
        "includeBotMessages": "0",
        "notifyOnlyMyMessages": "0",
        "notifyOnlyFPMessages": "0",
        "notifyOnlyBotMessages": "0",
        "showImageName": "1"
    },
    "Greetings": {
        "ignoreSystemMessages": "0",
        "sendGreetings": "0",
        "greetingsText": "Привет, $chat_name!",
        "greetingsCooldown": "2"
    },
    "OrderConfirm": {
        "watermark": "1",
        "sendReply": "0",
        "replyText": "$username, спасибо за подтверждение заказа $order_id!\nЕсли не сложно, оставь, пожалуйста, отзыв!"
    },
    "ReviewReply": {
        "star1Reply": "0",
        "star2Reply": "0",
        "star3Reply": "0",
        "star4Reply": "0",
        "star5Reply": "0",
        "star1ReplyText": "",
        "star2ReplyText": "",
        "star3ReplyText": "",
        "star4ReplyText": "",
        "star5ReplyText": "",
    },
    "Proxy": {
        "enable": "0",
        "ip": "",
        "port": "",
        "login": "",
        "password": "",
        "check": "0",
        "checkInterval": "3600"
    },
    "Other": {
        "watermark": "🧠 𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙 🤖",
        "requestsDelay": "4",
        "language": "ru"
    },
    "OrderControl": {
        "notify_pending_execution": "1",
        "pending_execution_threshold_m": "60",
        "notify_pending_confirmation": "1",
        "pending_confirmation_threshold_h": "24"
    }
}


def create_configs():
    if not os.path.exists("configs/auto_response.cfg"):
        with open("configs/auto_response.cfg", "w", encoding="utf-8"):
            ...

    if not os.path.exists("configs/auto_delivery.cfg"):
        with open("configs/auto_delivery.cfg", "w", encoding="utf-8"):
            ...


def create_config_obj(settings) -> ConfigParser:
    """
    Создает объект конфига с нужными настройками.

    :param settings: dict настроек.

    :return: объект конфига.
    """
    config = ConfigParser(delimiters=(":",), interpolation=None, allow_no_value=True)
    config.optionxform = str
    config.read_dict(settings)
    return config


def contains_russian(text: str) -> bool:
    for char in text:
        if 'А' <= char <= 'я' or char in 'Ёё':
            return True
    return False


def first_setup():
    config = create_config_obj(default_config)
    sleep_time = 1

    print(f"{Fore.CYAN}{Style.BRIGHT}Привет! Это FunPay Cortex! {Fore.RED}(`-`)/{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Не могу найти основной конфиг... {Fore.RED}(-_-;). . .{Style.RESET_ALL}")
    time.sleep(sleep_time)

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Давай проведем первичную настройку! {Fore.RED}°++°{Style.RESET_ALL}")
    time.sleep(sleep_time)

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Для начала введи токен (golden_key) твоего FunPay аккаунта (посмотреть его можно в расширении EditThisCookie) {Fore.RED}(._.){Style.RESET_ALL}")
        golden_key = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if len(golden_key) != 32:
            print(
                f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат токена. Попробуй еще раз! {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        config.set("FunPayAccount_Default", "golden_key", golden_key)
        break

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Если хочешь, ты можешь указать свой User-agent (введи в Google \"my user agent\"). Или можешь просто нажать Enter. "
              f"{Fore.RED}¯\\_(°_o)_/¯{Style.RESET_ALL}")
        user_agent = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if contains_russian(user_agent):
            print(
                f"\n{Fore.CYAN}{Style.BRIGHT}User-agent обычно не содержит русских букв. Уверен? Если да, введи еще раз, или оставь пустым. {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            confirm_ua = input(f"{Fore.MAGENTA}{Style.BRIGHT}Повтори User-agent или нажми Enter, чтобы пропустить: {Style.RESET_ALL}").strip()
            if confirm_ua != user_agent and confirm_ua != "":
                continue
            user_agent = confirm_ua
        if user_agent:
            config.set("FunPayAccount_Default", "user_agent", user_agent)
        break

    while True:
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Введи API-токен Telegram-бота (получить его можно у @BotFather). "
            f"@username бота должен начинаться с \"funpay\" (рекомендация, не строго). {Fore.RED}(._.){Style.RESET_ALL}")
        token = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        try:
            if not token or not token.split(":")[0].isdigit():
                raise ValueError("Неправильный формат токена")
            test_bot = telebot.TeleBot(token, threaded=False)
            username = test_bot.get_me().username
        except Exception as ex:
            s = ""
            if str(ex):
                s = f" ({str(ex)})"
            print(f"\n{Fore.CYAN}{Style.BRIGHT}Ошибка проверки токена. Попробуй еще раз!{s} {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        break

    while True:
        print(
            f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}Придумай пароль для доступа к Telegram ПУ. Пароль должен содержать >8 символов, заглавные, строчные буквы и цифру. "
            f" {Fore.RED}ᴖ̮ ̮ᴖ{Style.RESET_ALL}")
        password = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if not (len(password) >= 8 and
                any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password)):
            print(
                f"\n{Fore.CYAN}{Style.BRIGHT}Пароль слишком простой или не соответствует требованиям. Попробуй еще раз! {Fore.RED}\\(!!˚0˚)/{Style.RESET_ALL}")
            continue
        break

    config.set("Telegram", "enabled", "1")
    config.set("Telegram", "token", token)
    config.set("Telegram", "secretKeyHash", hash_password(password))

    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
          f"Теперь можно настроить ключ регистрации для менеджеров. Этот ключ они будут вводить боту для получения ограниченного доступа.\n"
          f"Если не хочешь настраивать это сейчас - просто нажми Enter. {Fore.RED}ᴖ̮ ̮ᴖ{Style.RESET_ALL}")
    manager_key = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
    if manager_key:
        config.set("Manager", "registration_key", manager_key)

    while True:
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}┌── {Fore.CYAN}"
              f"Если хочешь использовать IPv4 прокси – укажи их в формате login:password@ip:port или ip:port. Если нет - просто нажми Enter. "
              f"{Fore.RED}(* ^ ω ^){Style.RESET_ALL}")
        proxy_input = input(f"{Fore.MAGENTA}{Style.BRIGHT}└───> {Style.RESET_ALL}").strip()
        if proxy_input:
            try:
                login, password_proxy, ip, port_proxy = validate_proxy(proxy_input)
                config.set("Proxy", "enable", "1")
                config.set("Proxy", "check", "1")
                config.set("Proxy", "login", login)
                config.set("Proxy", "password", password_proxy)
                config.set("Proxy", "ip", ip)
                config.set("Proxy", "port", str(port_proxy))
                break
            except ValueError as e:
                print(
                    f"\n{Fore.CYAN}{Style.BRIGHT}Неверный формат прокси ({e}). Попробуй еще раз! {Fore.RED}(o-_-o){Style.RESET_ALL}")
                continue
        else:
            break

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Готово! Сейчас я сохраню конфиг и завершу программу! "
          f"{Fore.RED}ʘ>ʘ{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Запусти меня снова (<code>python main.py</code> или <code>Start.bat</code>) и напиши своему Telegram-боту. "
          f"Все остальное ты сможешь настроить через него. {Fore.RED}ʕ•ᴥ•ʔ{Style.RESET_ALL}")
    with open("configs/_main.cfg", "w", encoding="utf-8") as f:
        config.write(f)
    create_configs() 
    time.sleep(10)

# END OF FILE FunPayCortex-main/first_setup.py