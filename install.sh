#!/bin/bash
# Выходим из скрипта, если любая команда завершилась с ошибкой
set -e

# Цвета для красивого вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Запуск установки FunPay Cortex ---${NC}"

# 1. Обновление пакетов Termux с автоматическим решением конфликтов
echo -e "\n${YELLOW}> Шаг 1/6: Обновление пакетов Termux...${NC}"
pkg update -y && pkg upgrade -y -o Dpkg::Options::="--force-confnew"

# 2. Установка необходимых зависимостей
echo -e "\n${YELLOW}> Шаг 2/6: Установка зависимостей (python, git, clang, libxml2, libxslt)...${NC}"
# Убираем суффиксы -dev, так как в Termux они не используются
pkg install python git clang libxml2 libxslt -y

# 3. Клонирование репозитория
# Удаляем старую папку, если она существует, чтобы избежать конфликтов
if [ -d "FunPayCortex" ]; then
    echo -e "\n${YELLOW}Обнаружена старая версия. Создаю резервную копию и удаляю...${NC}"
    mv FunPayCortex "FunPayCortex_backup_$(date +%F_%T)"
fi

echo -e "\n${YELLOW}> Шаг 3/6: Клонирование репозитория FunPay Cortex...${NC}"
git clone https://github.com/Beedgee/FunPayCortex.git
cd FunPayCortex

# 4. Создание и активация виртуального окружения
echo -e "\n${YELLOW}> Шаг 4/6: Создание виртуального окружения...${NC}"
python -m venv venv

# 5. Установка зависимостей Python из requirements.txt
echo -e "\n${YELLOW}> Шаг 5/6: Установка зависимостей Python...${NC}"
source venv/bin/activate
# lxml и bcrypt требуют компиляции, лучше поставить их до requirements, чтобы ошибки были более очевидны
pip install lxml bcrypt
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

echo -e "\n${GREEN}--- Установка успешно завершена! ---${NC}"
echo -e "Для первого запуска и настройки бота, введите в консоль:${YELLOW}"
echo -e "cd ~/FunPayCortex && source venv/bin/activate && python main.py${NC}"
echo -e "\nДля всех последующих запусков, просто используйте команду:${YELLOW}"
echo -e "./start-cortex.sh${NC}"
