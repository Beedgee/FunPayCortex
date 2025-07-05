#!/bin/bash
# ==============================================================
#  УНИВЕРСАЛЬНЫЙ СКРИПТ УСТАНОВКИ FunPay Cortex ДЛЯ TERMUX
#  Версия от 2024-07-05
# ==============================================================
set -e

echo "🚀 Начало установки FunPay Cortex (универсальная версия)..."

# ШАГ 0: Рекомендуем запускать из домашней директории
cd $HOME

# ШАГ 1: Обновление пакетов и установка основных зависимостей
echo "🔧 Обновление репозиториев и установка Python/Git..."
pkg update -y && pkg upgrade -y
pkg install -y python git

# Иногда pip не ставится автоматически
if ! command -v pip &> /dev/null; then
    echo "⚙️ Установка pip вручную..."
    python -m ensurepip --upgrade || pkg install -y python-pip
fi

# ШАГ 2: Установка зависимостей для сборки C-расширений
echo "🛠️ Установка зависимостей для сборки (clang, libffi, openssl, rust, wheel)..."
pkg install -y clang libffi openssl rust

pip install --upgrade wheel setuptools

# ШАГ 3: Клонирование репозитория
if [ ! -d "FunPayCortex" ]; then
    echo "📂 Клонирование репозитория FunPayCortex..."
    git clone https://github.com/Beedgee/FunPayCortex.git
else
    echo "✅ Папка FunPayCortex уже существует. Пропускаем клонирование."
fi

cd FunPayCortex

# ШАГ 4: Удаляем старое окружение, если оно битое
if [ -d "venv" ]; then
    echo "⚠️ Старое venv обнаружено. Удаляем для чистой установки..."
    rm -rf venv
fi

# ШАГ 5: Создание и активация виртуального окружения
echo "🐍 Создание виртуального окружения Python..."
python -m venv venv

# Иногда в Termux нужно активировать так:
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Не найден файл venv/bin/activate. Установка прервана."
    exit 1
fi

# ШАГ 6: Апгрейд pip и установка зависимостей
pip install --upgrade pip
pip install --upgrade wheel setuptools
pip install -r requirements.txt

echo ""
echo "🎉 Установка успешно завершена!"
echo "✅ Все зависимости установлены, включая bcrypt."
echo ""
echo "👉 Для запуска бота используйте команды:"
echo "   1. cd ~/FunPayCortex"
echo "   2. source venv/bin/activate"
echo "   3. python main.py"
echo ""
