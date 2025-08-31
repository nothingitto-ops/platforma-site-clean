# Исправление счетчика изображений и свайпов в галерее

## Проблемы, которые были исправлены:

### 1. Счетчик изображений не обновлялся при листании
**Проблема:** При свайпах и кликах по изображениям счетчик оставался на "1/8" или показывал неправильные значения.

**Решение:** Добавлены вызовы `updateMobileImageCounter()` во все функции листания:
- `handleMobileViewerClick()` - для кликов по изображению в мобильной модалке
- `handleMobileZoomClick()` - для кликов по изображению в зум режиме
- `fullscreenImg._fullscreenTouchEnd()` - для свайпов в полноразмерной галерее

### 2. Конфликт между кликами и свайпами
**Проблема:** Клик по изображению для открытия полноразмерной галереи конфликтовал со свайпами для листания.

**Решение:** Добавлена логика различения кликов и свайпов:
- Отслеживание начальной позиции касания
- Проверка расстояния движения (больше 10px = свайп)
- Проверка длительности касания (больше 300ms = не клик)

### 3. Синхронизация счетчиков между режимами
**Проблема:** Счетчик не синхронизировался между обычной модалкой, зум режимом и полноразмерной галереей.

**Решение:** Добавлены вызовы всех функций обновления счетчиков:
- `updateMobileImageCounter()` - для основной модалки
- `updateZoomDots()` - для зум режима
- `updateFullscreenCounter()` - для полноразмерной галереи

## Технические детали:

### Функции обновления счетчиков:
```javascript
function updateMobileImageCounter() {
  const mobileDots = document.getElementById('mobileDots');
  if (mobileDots && current && current.images.length > 1) {
    mobileDots.textContent = `${curIndex + 1} / ${current.images.length}`;
  }
}

function updateZoomDots() {
  const zoomDotsContainer = document.getElementById('mobileZoomDots');
  if (zoomDotsContainer && current && current.images.length > 1) {
    zoomDotsContainer.textContent = `${curIndex + 1} / ${current.images.length}`;
  }
}

function updateFullscreenCounter() {
  const fullscreenCounter = document.getElementById('fullscreenCounter');
  if (fullscreenCounter && current) {
    if (current.images.length > 1) {
      fullscreenCounter.style.display = 'block';
      fullscreenCounter.textContent = `${curIndex + 1} / ${current.images.length}`;
    } else {
      fullscreenCounter.style.display = 'none';
    }
  }
}
```

### Логика различения кликов и свайпов:
```javascript
// Отслеживание начала касания
mobileMainImage.addEventListener('touchstart', (e) => {
  if (e.touches.length === 1) {
    clickStartX = e.touches[0].clientX;
    clickStartY = e.touches[0].clientY;
    clickStartTime = Date.now();
    isClick = true;
  }
}, { passive: true });

// Проверка движения
mobileMainImage.addEventListener('touchmove', (e) => {
  if (e.touches.length === 1) {
    const deltaX = Math.abs(currentX - clickStartX);
    const deltaY = Math.abs(currentY - clickStartY);
    
    if (deltaX > 10 || deltaY > 10) {
      isClick = false; // Это свайп, не клик
    }
  }
}, { passive: true });

// Проверка в обработчике клика
mobileMainImage.addEventListener('click', (e) => {
  const clickDuration = Date.now() - clickStartTime;
  
  if (isClick && clickDuration < 300) {
    openFullscreenGallery(e); // Только если это действительно клик
  }
});
```

## Результат:
✅ Счетчик изображений корректно работает во всех режимах просмотра
✅ Свайпы для листания работают без конфликтов с кликами
✅ Счетчики синхронизированы между всеми режимами просмотра
✅ Улучшена отзывчивость интерфейса

## Дата исправления:
2025-08-17
