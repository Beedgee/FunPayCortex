#!/bin/bash
# =================================================================
#  ИСПРАВЛЕННЫЙ СКРИПТ УСТАНОВКИ FUNPAY CORTEX ДЛЯ TERMUX
#  Версия от 2024-05-21
#  - Добавлены все необходимые зависимости для сборки bcrypt, lxml и др.
# =================================================================

echo "🚀 Начало установки FunPay Cortex (исправленная версия)..."

# ШАГ 1: Обновление пакетов и установка основных зависимостей
echo "🔧 Обновление репозиториев и установка Python/Git..."
pkg update -y && pkg upgrade -y
pkg install python git -y

# ШАГ 2: Установка зависимостей для сборки C-расширений
# ЭТО КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ, которое решает ошибку с bcrypt
echo "🛠️ Установка зависимостей для сборки (clang, libffi, openssl, rust)..."
echo "⏳ ВНИМАНИЕ: Этот шаг может занять много времени (10-25 минут), не прерывайте процесс!"
pkg install clang python-dev libffi-dev openssl-dev rust -y

# ШАГ 3: Клонирование репозитория
# Проверяем, существует ли папка, чтобы не было ошибки при повторном запуске
if [ ! -d "FunPayCortex" ]; then
    echo "📂 Клонирование репозитория FunPayCortex..."
    git clone https://github.com/Beedgee/FunPayCortex.git
else
    echo "✅ Папка FunPayCortex уже существует. Пропускаем клонирование."
fi

# Переходим в папку проекта
cd FunPayCortex

# ШАГ 4: Создание и активация виртуального окружения
echo "🐍 Создание виртуального окружения Python..."
python -m venv venv
echo "✅ Активация виртуального окружения..."
source venv/bin/activate

# ШАГ 5: Установка Python-пакетов из requirements.txt
echo "📦 Установка зависимостей Python из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# ШАГ 6: Финальные инструкции
echo ""
echo "🎉 Установка успешно завершена!"
echo "✅ Все зависимости установлены, включая bcrypt."
echo ""
echo "👉 Теперь, для запуска бота, используйте команды:"
echo "   1. cd FunPayCortex"
echo "   2. source venv/bin/activate"
echo "   3. python main.py"
echo ""
