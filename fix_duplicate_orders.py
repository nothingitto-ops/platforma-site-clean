#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def fix_duplicate_orders():
    """Исправляет дубли в order для каждого раздела"""
    
    # Загружаем данные
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Загружено {len(products)} товаров")
    
    # Группируем товары по разделам
    sections = defaultdict(list)
    for product in products:
        section = product.get('section', 'home')
        sections[section].append(product)
    
    print(f"Найдено разделов: {list(sections.keys())}")
    
    # Исправляем order для каждого раздела
    fixed_count = 0
    for section, section_products in sections.items():
        print(f"\nОбрабатываем раздел '{section}' ({len(section_products)} товаров)")
        
        # Сортируем по order, затем по id для стабильности
        section_products.sort(key=lambda x: (x.get('order', 0), x.get('id', 0)))
        
        # Проверяем на дубли
        orders = [p.get('order', 0) for p in section_products]
        duplicates = [x for x in set(orders) if orders.count(x) > 1]
        
        if duplicates:
            print(f"  Найдены дубли в order: {duplicates}")
            
            # Переназначаем order последовательно
            for i, product in enumerate(section_products, 1):
                old_order = product.get('order', 0)
                product['order'] = i
                if old_order != i:
                    print(f"    {product.get('title', 'Unknown')}: order {old_order} -> {i}")
                    fixed_count += 1
        else:
            print(f"  Дублей не найдено")
    
    # Сохраняем исправленные данные
    if fixed_count > 0:
        # Сортируем все товары по разделу и order
        all_products = []
        for section in sorted(sections.keys()):
            all_products.extend(sections[section])
        
        # Сортируем по разделу и order
        all_products.sort(key=lambda x: (x.get('section', ''), x.get('order', 0)))
        
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Исправлено {fixed_count} дублей в order")
        print("Файл products.json обновлен")
    else:
        print("\n✅ Дублей не найдено, файл не изменен")
    
    return fixed_count

if __name__ == "__main__":
    fix_duplicate_orders()
