#!/bin/bash

# Скрипт для обновления данных товаров Platforma.sluchay

echo "🛍️ Обновление данных товаров Platforma.sluchay..."

# Проверяем, что мы в правильной директории
if [ ! -f "products.json" ]; then
    echo "❌ Ошибка: products.json не найден. Убедитесь, что вы в корневой папке проекта."
    exit 1
fi

# Обновляем версию для кэш-бастинга
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "📅 Текущее время: $TIMESTAMP"

# Обновляем версию в index.html
sed -i.bak "s/v=.*&nocache=1/v=PRODUCTS_${TIMESTAMP}&nocache=1/g" index.html
sed -i.bak "s/timestamp=.*&cache=KILLED/timestamp=${TIMESTAMP}&cache=KILLED/g" index.html

# Удаляем временные файлы
rm -f index.html.bak

# Добавляем только файлы данных
echo "📝 Добавляем изменения в git..."
git add products.json index.html

# Создаем коммит
COMMIT_MESSAGE="🛍️ Обновление данных товаров - $(date '+%d.%m.%Y %H:%M:%S')"
echo "💾 Создаем коммит: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

# Отправляем на GitHub
echo "🚀 Отправляем на GitHub..."
git push origin main

echo "✅ Обновление товаров завершено!"
echo "🌐 Сайт будет доступен через несколько минут на: https://platformasluchay.ru"
