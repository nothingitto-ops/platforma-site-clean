#!/bin/bash

# Скрипт для загрузки изображений на GitHub по одному

echo "🖼️ Загрузка изображений на GitHub..."

# Проверяем, что мы в правильной директории
if [ ! -f "index.html" ]; then
    echo "❌ Ошибка: index.html не найден. Убедитесь, что вы в корневой папке проекта."
    exit 1
fi

# Создаем список всех изображений, отсортированных по размеру
echo "📋 Создаем список изображений..."
find img/ -name "*.jpg" -exec ls -lh {} \; | sort -k5 -n > image_list.txt

# Читаем список и загружаем по одному
while IFS= read -r line; do
    if [[ $line =~ img/.*\.jpg ]]; then
        image_path=$(echo "$line" | awk '{print $9}')
        size=$(echo "$line" | awk '{print $5}')
        
        echo "📤 Загружаем: $image_path ($size)"
        
        # Добавляем изображение в git
        git add "$image_path"
        
        # Создаем коммит
        git commit -m "🖼️ Add image: $image_path ($size)"
        
        # Отправляем на GitHub
        if git push; then
            echo "✅ Успешно загружено: $image_path"
            sleep 2  # Небольшая пауза между загрузками
        else
            echo "❌ Ошибка загрузки: $image_path"
            echo "🔄 Пропускаем и продолжаем..."
            git reset --soft HEAD~1
            continue
        fi
    fi
done < image_list.txt

# Удаляем временный файл
rm -f image_list.txt

echo "✅ Загрузка изображений завершена!"
echo "🌐 Сайт будет доступен через несколько минут на: https://platformasluchay.ru"
