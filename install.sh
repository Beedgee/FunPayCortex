#!/bin/bash
# Выходим из скрипта, если любая команда завершилась с ошибкой
set -e

# Цвета для красивого вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Запуск установки FunPay Cortex ---${NC}"
sleep 1

# 1. Обновление пакетов Termux с автоматическим решением конфликтов
echo -e "\n${YELLOW}> Шаг 1/6: Обновление пакетов Termux...${NC}"
pkg update -y && pkg upgrade -y -o Dpkg::Options::="--force-confnew"

# 2. Установка необходимых системных зависимостей
echo -e "\n${YELLOW}> Шаг 2/6: Установка системных зависимостей...${NC}"
echo -e "${RED}ВНИМАНИЕ:${NC} Этот шаг может занять ${YELLOW}10-20 минут${NC}, особенно установка 'rust'. Пожалуйста, не закрывайте Termux."
sleep 3
# Добавляем 'rust' для компиляции bcrypt и 'libjpeg-turbo' для Pillow
pkg install python git clang libxml2 libxslt rust libjpeg-turbo -y

# 3. Клонирование репозитория
# Удаляем старую папку, если она существует, чтобы избежать конфликтов
if [ -d "FunPayCortex" ]; then
    echo -e "\n${YELLOW}Обнаружена старая версия. Создаю резервную копию и удаляю...${NC}"
    mv FunPayCortex "FunPayCortex_backup_$(date +%F_%T)"
fi

echo -e "\n${YELLOW}> Шаг 3/6: Клонирование репозитория FunPay Cortex...${NC}"
git clone https://github.com/Beedgee/FunPayCortex.git
cd FunPayCortex

# 4. Создание виртуального окружения
echo -e "\n${YELLOW}> Шаг 4/6: Создание виртуального окружения...${NC}"
python -m venv venv

# 5. Установка зависимостей Python из requirements.txt
echo -e "\n${YELLOW}> Шаг 5/6: Установка зависимостей Python...${NC}"
source venv/bin/activate
# Обновим pip на всякий случай
pip install --upgrade pip
# Устанавливаем зависимости
pip install -r requirements.txt
deactivate

# 6. Создание скрипта для удобного запуска
echo -e "\n${YELLOW}> Шаг 6/6: Создание скрипта для запуска (start-cortex.sh)...${NC}"
# Создаем файл start.sh в главной директории Termux (~)
cat > ~/start-cortex.sh <<EOL
#!/bin/bash
cd \$(dirname \$0)/FunPayCortex
source venv/bin/activate
python main.py
EOL

# Делаем скрипт исполняемым
chmod +x ~/start-cortex.sh

# --- Финальное сообщение ---
echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN} ✅ Установка FunPay Cortex успешно завершена! ✅ ${NC}"
echo -e "${GREEN}===============================================${NC}"
sleep 1

echo -e "\n${YELLOW}--- ЧТО ДЕЛАТЬ ДАЛЬШЕ? ---${NC}"
echo -e "\n1. ${GREEN}Первый запуск и настройка:${NC}"
echo -e "   После установки вам нужно запустить бота в первый раз, чтобы он создал конфиги и вы могли его настроить."
echo -e "   Скопируйте и вставьте в консоль команду ниже:"
echo -e "\n   ${YELLOW}cd ~/FunPayCortex && source venv/bin/activate && python main.py${NC}\n"
echo -e "   Следуйте инструкциям в консоли (ввод токенов и т.д.)."
sleep 1

echo -e "\n2. ${GREEN}Все последующие запуски:${NC}"
echo -e "   После первой настройки, для всех будущих запусков используйте короткую и удобную команду:"
echo -e "\n   ${YELLOW}./start-cortex.sh${NC}\n"
echo -e "   (Ее нужно вводить в домашней директории Termux, куда вы попадаете при открытии приложения)."
echo -e "\n${GREEN}Удачной автоматизации! 🚀${NC}"
