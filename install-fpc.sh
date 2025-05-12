#!/bin/bash

# START OF FILE FunPayCortex/install-fpc.sh # Consider renaming the script itself?

# --- Configuration ---
# Repository URL (!!! CHANGE THIS TO YOUR REPOSITORY URL OR REMOVE GIT CLONE PART IF USING ARCHIVE !!!)
REPO_URL="YOUR_GITHUB_REPOSITORY_URL/FunPayCortex.git"
# Directory name for the bot
BOT_DIR="FunPayCortex"
# Username for the bot service (will be created if doesn't exist)
BOT_USER="cortexuser" # Changed username suggestion
# Service file name in the repository
SERVICE_FILE_REPO="FunPayCortex@.service" # Changed service file name
# Service name on the system
SERVICE_NAME="funpaycortex" # Changed service name (lowercase recommended for systemd)
# --- End Configuration ---

# Function to print messages
print_msg() {
    echo "--------------------------------------------------"
    echo "$1"
    echo "--------------------------------------------------"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    print_msg "Этот скрипт должен быть запущен от имени суперпользователя (root). Используйте 'sudo bash install-fpc.sh'"
    exit 1
fi

# Update system and install dependencies
print_msg "Обновление системы и установка зависимостей..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git wget sudo

# Create user if not exists
if id "$BOT_USER" &>/dev/null; then
    print_msg "Пользователь '$BOT_USER' уже существует."
else
    print_msg "Создание пользователя '$BOT_USER'..."
    adduser --disabled-password --gecos "" "$BOT_USER"
    # Add user to sudo group to allow service management (optional, consider security implications)
    # usermod -aG sudo "$BOT_USER"
    # print_msg "Пользователь '$BOT_USER' добавлен в группу sudo."
    print_msg "Пользователь '$BOT_USER' создан."
fi

# Switch to user home directory
USER_HOME=$(eval echo "~$BOT_USER")
cd "$USER_HOME" || { print_msg "Не удалось перейти в домашнюю директорию пользователя '$BOT_USER'."; exit 1; }

# Clone repository or check if directory exists
if [ -d "$BOT_DIR" ]; then
    print_msg "Директория '$BOT_DIR' уже существует. Пропуск клонирования."
    cd "$BOT_DIR" || { print_msg "Не удалось перейти в директорию '$BOT_DIR'."; exit 1; }
else
    print_msg "Клонирование репозитория '$REPO_URL'..."
    sudo -u "$BOT_USER" git clone "$REPO_URL" "$BOT_DIR"
    cd "$BOT_DIR" || { print_msg "Не удалось перейти в директорию '$BOT_DIR'."; exit 1; }
fi

# Create and activate virtual environment
print_msg "Создание виртуального окружения..."
sudo -u "$BOT_USER" python3 -m venv pyvenv
# Note: Activation is for the current script session, the service will call the venv python directly

# Install requirements
print_msg "Установка зависимостей из requirements.txt..."
sudo -u "$BOT_USER" "$USER_HOME/$BOT_DIR/pyvenv/bin/pip" install -r requirements.txt

# Initial setup if config doesn't exist
if [ ! -f "configs/_main.cfg" ]; then
    print_msg "Основной конфигурационный файл не найден. Запускаем первичную настройку..."
    # Run setup as the bot user
    sudo -u "$BOT_USER" "$USER_HOME/$BOT_DIR/pyvenv/bin/python" main.py
    if [ $? -ne 0 ]; then
         print_msg "Ошибка во время первичной настройки. Пожалуйста, проверьте вывод выше."
         # exit 1 # Don't exit, let user retry maybe?
    else
         print_msg "Первичная настройка завершена."
    fi
else
    print_msg "Конфигурационный файл найден, пропуск первичной настройки."
fi

# Setup systemd service
print_msg "Настройка сервиса systemd..."
SERVICE_FILE_PATH="/etc/systemd/system/${SERVICE_NAME}@.service"

if [ ! -f "$SERVICE_FILE_REPO" ]; then
    print_msg "Ошибка: Файл сервиса '$SERVICE_FILE_REPO' не найден в репозитории!"
    # Optionally, create a default service file here if needed
    exit 1
fi

# Copy service file
cp "$SERVICE_FILE_REPO" "$SERVICE_FILE_PATH"

# Replace placeholder user if necessary (already done in file)
# sed -i "s/%i/$BOT_USER/g" "$SERVICE_FILE_PATH" # No longer needed if %i is used correctly

# Reload systemd, enable and start the service
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}@${BOT_USER}.service"
systemctl start "${SERVICE_NAME}@${BOT_USER}.service"

print_msg "Сервис '${SERVICE_NAME}@${BOT_USER}' настроен и запущен."
print_msg "Проверить статус: systemctl status ${SERVICE_NAME}@${BOT_USER}.service"
print_msg "Посмотреть логи: journalctl -u ${SERVICE_NAME}@${BOT_USER}.service -f"
print_msg "Установка завершена!"

# Deactivate venv (for current script session)
# deactivate # Not needed as we didn't activate globally

exit 0

# END OF FILE FunPayCortex/install-fpc.sh