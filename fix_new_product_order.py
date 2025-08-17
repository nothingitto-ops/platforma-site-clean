#!/usr/bin/env python3
import json
from datetime import datetime

def fix_new_product_order():
    """Исправляет порядок так, чтобы новый товар был первым"""
    
    # Загружаем данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Загружено {len(products)} товаров")
    
    # Группируем товары по разделам
    sections = {}
    for product in products:
        section = product.get('section', 'home')
        if section not in sections:
            sections[section] = []
        sections[section].append(product)
    
    print(f"Найдено разделов: {list(sections.keys())}")
    
    # Исправляем порядок для каждого раздела
    for section, section_products in sections.items():
        print(f"\nОбрабатываем раздел '{section}' ({len(section_products)} товаров)")
        
        # Сортируем по дате создания (новые сначала)
        section_products.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        # Переназначаем order (новые товары получают меньшие номера)
        for i, product in enumerate(section_products, 1):
            old_order = product.get('order', 0)
            product['order'] = i
            created_date = product.get('created', 'Unknown')
            print(f"  {product.get('title', 'Unknown')}: order {old_order} -> {i} (создан: {created_date})")
    
    # Сортируем все товары по разделу и order
    all_products = []
    for section in sorted(sections.keys()):
        all_products.extend(sections[section])
    
    # Сортируем по разделу и order
    all_products.sort(key=lambda x: (x.get('section', ''), x.get('order', 0)))
    
    # Сохраняем исправленные данные
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Порядок исправлен - новые товары теперь первые")
    print("Файл products.json обновлен")

if __name__ == "__main__":
    fix_new_product_order()
