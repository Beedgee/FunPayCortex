#!/bin/bash
# Установка FunPay Cortex в Termux с исправлением зависимостей для сборки

echo "🚀 Начало установки FunPay Cortex..."

# Обновляем пакеты и устанавливаем основные зависимости
echo "🔧 Обновление пакетов и установка основных зависимостей..."
pkg update -y && pkg upgrade -y
pkg install python git -y

# ВАЖНО: Устанавливаем зависимости для сборки C-расширений (включая bcrypt, lxml)
echo "🛠️ Установка зависимостей для сборки (clang, libffi, openssl, rust)..."
pkg install clang python-dev libffi-dev openssl-dev rust -y

# Клонируем репозиторий, если папки еще нет
if [ ! -d "FunPayCortex" ]; then
    echo "📂 Клонирование репозитория FunPayCortex..."
    git clone https://github.com/Beedgee/FunPayCortex.git
else
    echo "✅ Папка FunPayCortex уже существует."
fi

cd FunPayCortex

# Создаем и активируем виртуальное окружение
echo "🐍 Создание виртуального окружения..."
python -m venv venv
echo "✅ Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем Python-пакеты из requirements.txt
echo "📦 Установка Python-пакетов из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎉 Установка успешно завершена!"
echo "👉 Теперь запустите бота командой: python main.py"
