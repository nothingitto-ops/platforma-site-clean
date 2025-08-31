# Правильный метод сжатия изображений для сайта

## Команда для сжатия:
```bash
mogrify -verbose -auto-orient -resize '2000x2000>' -strip -interlace Plane -quality 82 img/product_X/*.jpg
```

## Параметры:
- `-auto-orient` - автоматическая ориентация
- `-resize '2000x2000>'` - максимальный размер 2000px (сохраняет пропорции)
- `-strip` - удаляет метаданные
- `-interlace Plane` - прогрессивная загрузка
- `-quality 82` - оптимальное качество сжатия

## Результат:
- Размер файлов: 150-400KB (идеально для веба)
- Качество: высокое, без видимых потерь
- Совместимость: все браузеры

## Использование:
1. Скопировать оригинальные изображения в папку `img/product_X/`
2. Применить команду сжатия
3. Обновить кэш браузера с временной меткой

## Пример:
```bash
# Для нового продукта
mkdir -p img/product_18
cp "/path/to/original/images/*.jpg" img/product_18/
mogrify -verbose -auto-orient -resize '2000x2000>' -strip -interlace Plane -quality 82 img/product_18/*.jpg
```
