#!/bin/bash

# Platforma.sluchay - Test Server Script
# Запуск локального тестового сервера

echo "🚀 Platforma.sluchay - Test Server"
echo "=================================="

# Проверяем, что мы в правильной директории
if [ ! -f "index.html" ]; then
    echo "❌ Ошибка: index.html не найден. Убедитесь, что вы в корневой папке проекта."
    exit 1
fi

echo "📍 Запуск тестового сервера на порту 8003..."
echo ""
echo "🌐 Ссылки:"
echo "   Основной сайт: http://localhost:8003/"
echo "   Simple Manager: http://localhost:8003/simple-manager.html (если есть)"
echo ""
echo "📱 Для тестирования на телефоне:"
echo "   http://$(ipconfig getifaddr en0):8003/"
echo ""
echo "⏹️  Для остановки нажмите Ctrl+C"
echo ""

# Запускаем сервер
python3 -m http.server 8003
