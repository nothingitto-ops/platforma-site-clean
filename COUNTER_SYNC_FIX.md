# Исправление синхронизации счетчиков изображений

## Проблема:
Счетчик в увеличенной галерее работал в обратную сторону по сравнению с обычной модалкой при одинаковых свайпах.

## Причина:
Разная формула расчета `deltaX` в разных режимах просмотра:

### ❌ Было (неправильно):
- **Мобильная модалка:** `deltaX = touchStartX - touchEndX`
- **Зум модалка:** `deltaX = touchStartX - touchEndX`  
- **Полноразмерная галерея:** `deltaX = endX - startX` ← **ОШИБКА!**

### ✅ Стало (исправлено):
- **Все режимы:** `deltaX = startX - endX` (или `touchStartX - touchEndX`)

## Исправления:

### 1. Исправлена формула в полноразмерной галерее
```javascript
// Было:
const deltaX = endX - startX;

// Стало:
const deltaX = startX - endX; // Синхронизировано с другими режимами
```

### 2. Создана универсальная функция обновления счетчиков
```javascript
function updateAllCounters() {
  updateMobileImageCounter();
  updateZoomDots();
  updateFullscreenCounter();
}
```

### 3. Заменены все вызовы на универсальную функцию
- `handleMobileViewerClick()` → `updateAllCounters()`
- `handleMobileZoomClick()` → `updateAllCounters()`
- `mobileMainImage._touchEndHandler` → `updateAllCounters()`
- `mobileZoomImg._swipeTouchEnd` → `updateAllCounters()`
- `fullscreenImg._fullscreenTouchEnd` → `updateAllCounters()`

## Результат:
✅ Все счетчики синхронизированы и работают в одном направлении
✅ Свайп влево = следующее изображение во всех режимах
✅ Свайп вправо = предыдущее изображение во всех режимах
✅ Счетчики обновляются мгновенно и синхронно

## Дата исправления:
2025-08-17
