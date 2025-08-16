#!/bin/bash

# Скрипт для автоматического обновления сайта через GitHub
# Обновляет сайт на https://platformasluchay.ru/

echo "🔄 Начинаем обновление сайта..."

# Проверяем статус git
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Обнаружены изменения, добавляем в git..."
    git add .
    
    # Создаем коммит с текущей датой и временем
    COMMIT_MESSAGE="Обновление сайта $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"
    
    echo "🚀 Отправляем изменения на GitHub..."
    git push origin main
    
    echo "✅ Сайт успешно обновлен!"
    echo "🌐 Проверьте изменения на https://platformasluchay.ru/"
else
    echo "ℹ️  Изменений не обнаружено"
fi

echo "✨ Готово!"
