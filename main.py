# START OF FILE FunPayCortex/main.py

import time
from pip._internal.cli.main import main

# todo убрать когда-то
while True:
    try:
        import lxml

        break
    except ModuleNotFoundError:
        main(["install", "-U", "lxml>=5.3.0"])
while True:
    try:
        import bcrypt

        break
    except ModuleNotFoundError:
        main(["install", "-U", "bcrypt>=4.2.0"])
import Utils.cortex_tools
import Utils.config_loader as cfg_loader
from first_setup import first_setup
from colorama import Fore, Style
from Utils.logger import LOGGER_CONFIG
import logging.config
import colorama
import sys
import os
from cortex import Cortex
import Utils.exceptions as excs
from locales.localizer import Localizer
import announcements

logo = r"""
 ______  _____    _____               _
|  ____||  __ \  / ____|             | |
| |__   | |__) || |       ___   _ __ | |_   ___ __  __
|  __|  |  ___/ | |      / _ \ | '__|| __| / _ \\ \/ /
| |     | |     | |____ | (_) || |   | |_ |  __/ >  <
|_|     |_|      \_____| \___/ |_|    \__| \___|/_/\_\

""" # ИСПРАВЛЕННЫЙ ЛОГОТИП FPCortex

VERSION = "0.1.15.22"

Utils.cortex_tools.set_console_title(f"FunPay Cortex v{VERSION}")

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

folders = ["configs", "logs", "storage", "storage/cache", "storage/plugins", "storage/products", "plugins"]
for i in folders:
    if not os.path.exists(i):
        os.makedirs(i)

files = ["configs/auto_delivery.cfg", "configs/auto_response.cfg"]
for i in files:
    if not os.path.exists(i):
        with open(i, "w", encoding="utf-8") as f:
            ...

colorama.init()

logging.config.dictConfig(LOGGER_CONFIG)
logging.raiseExceptions = False
logger = logging.getLogger("main")
logger.debug("------------------------------------------------------------------")

print(f"{Style.RESET_ALL}{Fore.CYAN}{logo}{Style.RESET_ALL}")
print(f"{Fore.RED}{Style.BRIGHT}v{VERSION}{Style.RESET_ALL}\n")
print(f"{Fore.MAGENTA}{Style.BRIGHT}Автор: {Fore.BLUE}{Style.BRIGHT}@beedge{Style.RESET_ALL}")


if not os.path.exists("configs/_main.cfg"):
    first_setup()
    sys.exit()

if sys.platform == "linux" and os.getenv('FPCORTEX_IS_RUNNIG_AS_SERVICE', '0') == '1':
    import getpass
    service_name = "FunPayCortex"
    run_dir = f"/run/{service_name}"
    user_run_dir = f"{run_dir}/{getpass.getuser()}"
    pid_file_path = f"{user_run_dir}/{service_name}.pid"

    if not os.path.exists(run_dir):
        os.makedirs(run_dir, mode=0o755)
    if not os.path.exists(user_run_dir):
         os.makedirs(user_run_dir, mode=0o755)

    try:
        pid = str(os.getpid())
        with open(pid_file_path, "w") as pidFile:
             pidFile.write(pid)
        logger.info(f"$GREENPID файл создан: {pid_file_path}, PID процесса: {pid}")
    except Exception as e:
         logger.error(f"Не удалось создать PID файл {pid_file_path}: {e}")


try:
    logger.info("$MAGENTAЗагружаю конфиг _main.cfg...")
    MAIN_CFG = cfg_loader.load_main_config("configs/_main.cfg")
    localizer = Localizer(MAIN_CFG["Other"]["language"])
    _ = localizer.translate

    logger.info("$MAGENTAЗагружаю конфиг auto_response.cfg...")
    AR_CFG = cfg_loader.load_auto_response_config("configs/auto_response.cfg")
    RAW_AR_CFG = cfg_loader.load_raw_auto_response_config("configs/auto_response.cfg")

    logger.info("$MAGENTAЗагружаю конфиг auto_delivery.cfg...")
    AD_CFG = cfg_loader.load_auto_delivery_config("configs/auto_delivery.cfg")
except excs.ConfigParseError as e:
    logger.error(e)
    logger.error("Завершаю программу...")
    time.sleep(5)
    sys.exit()
except UnicodeDecodeError:
    logger.error("Произошла ошибка при расшифровке UTF-8. Убедитесь, что кодировка файла = UTF-8, "
                 "а формат конца строк = LF.")
    logger.error("Завершаю программу...")
    time.sleep(5)
    sys.exit()
except:
    logger.critical("Произошла непредвиденная ошибка.")
    logger.warning("TRACEBACK", exc_info=True)
    logger.error("Завершаю программу...")
    time.sleep(5)
    sys.exit()

localizer = Localizer(MAIN_CFG["Other"]["language"])

try:
    Cortex(MAIN_CFG, AD_CFG, AR_CFG, RAW_AR_CFG, VERSION).init().run()
except KeyboardInterrupt:
    logger.info("Завершаю программу...")
    sys.exit()
except:
    logger.critical("При работе Кортекса произошла необработанная ошибка.")
    logger.warning("TRACEBACK", exc_info=True)
    logger.critical("Завершаю программу...")
    time.sleep(5)
    sys.exit()

# END OF FILE FunPayCortex/main.py