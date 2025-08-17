#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import shutil
from PIL import Image, ImageTk
import re
from datetime import datetime

class CleanCatalogManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🛍️ Platforma Catalog Manager")
        self.root.geometry("1000x700")
        
        # Данные
        self.products = []
        self.selected_images = []
        self.load_products()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Главный контейнер с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Управление товарами
        products_frame = ttk.Frame(notebook)
        notebook.add(products_frame, text="📦 Товары")
        self.setup_products_tab(products_frame)
        
        # Вкладка 2: Добавление товара
        add_frame = ttk.Frame(notebook)
        notebook.add(add_frame, text="➕ Добавить товар")
        self.setup_add_tab(add_frame)
        
        # Вкладка 3: Деплой
        deploy_frame = ttk.Frame(notebook)
        notebook.add(deploy_frame, text="🚀 Деплой")
        self.setup_deploy_tab(deploy_frame)
        
    def setup_products_tab(self, parent):
        """Настройка вкладки с товарами"""
        # Верхняя панель с фильтрами
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Фильтр по секциям
        ttk.Label(top_frame, text="Раздел:").pack(side=tk.LEFT, padx=(0, 5))
        self.section_var = tk.StringVar(value="all")
        section_combo = ttk.Combobox(top_frame, textvariable=self.section_var, 
                                   values=["all", "home", "nessffo"], width=10)
        section_combo.pack(side=tk.LEFT, padx=5)
        section_combo.bind('<<ComboboxSelected>>', self.filter_products)
        
        # Кнопки управления
        ttk.Button(top_frame, text="🔄 Обновить", 
                  command=self.refresh_products_list).pack(side=tk.RIGHT, padx=5)
        
        # Основной контейнер
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Левая панель - список товаров
        left_frame = ttk.LabelFrame(main_frame, text="📋 Список товаров", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Список товаров
        columns = ("order", "section", "title", "price", "status", "images")
        self.products_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        self.products_tree.heading("order", text="№")
        self.products_tree.heading("section", text="Раздел")
        self.products_tree.heading("title", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("status", text="Статус")
        self.products_tree.heading("images", text="Фото")
        
        self.products_tree.column("order", width=40)
        self.products_tree.column("section", width=80)
        self.products_tree.column("title", width=200)
        self.products_tree.column("price", width=80)
        self.products_tree.column("status", width=80)
        self.products_tree.column("images", width=60)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления товарами
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_product, width=15).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="🗑️ Удалить", 
                  command=self.delete_product, width=15).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="⬆️ Вверх", 
                  command=self.move_product_up, width=10).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="⬇️ Вниз", 
                  command=self.move_product_down, width=10).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Правая панель - просмотр товара
        right_frame = ttk.LabelFrame(main_frame, text="👁️ Просмотр товара", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Информация о товаре
        info_frame = ttk.LabelFrame(right_frame, text="📝 Информация о товаре", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Поля для редактирования
        ttk.Label(info_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.edit_title_entry = ttk.Entry(info_frame, width=30)
        self.edit_title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.edit_price_entry = ttk.Entry(info_frame, width=30)
        self.edit_price_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.edit_desc_entry = ttk.Entry(info_frame, width=30)
        self.edit_desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Мета:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.edit_meta_entry = ttk.Entry(info_frame, width=30)
        self.edit_meta_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Раздел:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.edit_section_var = tk.StringVar()
        self.edit_section_combo = ttk.Combobox(info_frame, textvariable=self.edit_section_var, 
                                             values=["home", "nessffo"], width=27)
        self.edit_section_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Статус:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.edit_status_var = tk.StringVar()
        self.edit_status_combo = ttk.Combobox(info_frame, textvariable=self.edit_status_var, 
                                            values=["stock", "preorder"], width=27)
        self.edit_status_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        # Кнопка сохранения изменений
        ttk.Button(info_frame, text="💾 Сохранить изменения", 
                  command=self.save_product_changes).grid(row=6, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Настройка весов
        info_frame.columnconfigure(1, weight=1)
        
        # Галерея изображений
        gallery_frame = ttk.LabelFrame(right_frame, text="🖼️ Изображения", padding="10")
        gallery_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas для изображений
        self.canvas = tk.Canvas(gallery_frame, bg='white')
        scrollbar_gallery = ttk.Scrollbar(gallery_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=scrollbar_gallery.set)
        
        self.canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar_gallery.pack(fill=tk.X)
        
        # Привязываем события
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
        self.refresh_products_list()
        
    def setup_add_tab(self, parent):
        """Настройка вкладки добавления товара"""
        # Форма
        form_frame = ttk.LabelFrame(parent, text="📝 Информация о товаре", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поля формы
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(form_frame, width=50)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.title_entry.bind('<Control-v>', self.paste_text)
        
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_entry = ttk.Entry(form_frame, width=50)
        self.desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.desc_entry.bind('<Control-v>', self.paste_text)
        
        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_entry = ttk.Entry(form_frame, width=50)
        self.price_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.price_entry.bind('<Control-v>', self.paste_text)
        
        ttk.Label(form_frame, text="Мета:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.meta_entry = ttk.Entry(form_frame, width=50)
        self.meta_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.meta_entry.bind('<Control-v>', self.paste_text)
        
        ttk.Label(form_frame, text="Раздел:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.section_entry_var = tk.StringVar(value="home")
        self.section_entry_combo = ttk.Combobox(form_frame, textvariable=self.section_entry_var, 
                                              values=["home", "nessffo"], width=47)
        self.section_entry_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Статус:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.status_entry_var = tk.StringVar(value="stock")
        self.status_entry_combo = ttk.Combobox(form_frame, textvariable=self.status_entry_var, 
                                             values=["stock", "preorder"], width=47)
        self.status_entry_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        # Настройка весов
        form_frame.columnconfigure(1, weight=1)
        
        # Панель изображений
        images_frame = ttk.LabelFrame(parent, text="📸 Изображения", padding="10")
        images_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Кнопки изображений
        img_btn_frame = ttk.Frame(images_frame)
        img_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(img_btn_frame, text="📸 Выбрать фото", 
                  command=self.select_images, width=15).pack(side=tk.LEFT, padx=5, pady=2)
        
        ttk.Button(img_btn_frame, text="⬆️", command=self.move_image_up, width=5).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(img_btn_frame, text="⬇️", command=self.move_image_down, width=5).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(img_btn_frame, text="❌", command=self.remove_image, width=5).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Список выбранных изображений
        self.images_listbox = tk.Listbox(images_frame, height=8)
        self.images_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопка сохранения
        self.save_btn = ttk.Button(parent, text="💾 Сохранить товар", 
                                  command=self.save_product, width=25)
        self.save_btn.pack(pady=10)
    
    def load_products(self):
        """Загрузка товаров из файла"""
        try:
            if os.path.exists('products.json'):
                with open('products.json', 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки товаров: {e}")
            self.products = []
    
    def save_products(self):
        """Сохранение товаров в файл"""
        try:
            with open('products.json', 'w', encoding='utf-8') as f:
                json.dump(self.products, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения товаров: {e}")
    
    def get_next_id(self):
        """Получение следующего ID"""
        if not self.products:
            return 1
        return max(p.get('id', 0) for p in self.products) + 1
    
    def get_next_order(self, section):
        """Получение следующего order для секции (всегда 1 для новых товаров)"""
        return 1
    
    def shift_orders_up(self, section):
        """Сдвигает все order в секции на +1"""
        section_products = [p for p in self.products if p.get('section') == section]
        # Сортируем по order для правильного сдвига
        section_products.sort(key=lambda x: x.get('order', 0), reverse=True)
        for product in section_products:
            product['order'] = product.get('order', 0) + 1
    
    def shift_orders_down(self, section, deleted_order):
        """Сдвигает order на -1 после удаления товара"""
        section_products = [p for p in self.products if p.get('section') == section]
        for product in section_products:
            if product.get('order', 0) > deleted_order:
                product['order'] = product.get('order', 0) - 1
    
    def fix_duplicate_orders(self, section):
        """Исправляет дубли в order для раздела"""
        section_products = [p for p in self.products if p.get('section') == section]
        if not section_products:
            return
        
        # Сортируем по дате создания (новые сначала)
        section_products.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        # Переназначаем order
        for i, product in enumerate(section_products, 1):
            product['order'] = i
    
    def fix_duplicate_orders(self):
        """Исправляет дубли в order для всех разделов"""
        from collections import defaultdict
        
        # Группируем товары по разделам
        sections = defaultdict(list)
        for product in self.products:
            section = product.get('section', 'home')
            sections[section].append(product)
        
        fixed_count = 0
        
        # Исправляем order для каждого раздела
        for section, section_products in sections.items():
            # Сортируем по order, затем по id для стабильности
            section_products.sort(key=lambda x: (x.get('order', 0), x.get('id', 0)))
            
            # Проверяем на дубли
            orders = [p.get('order', 0) for p in section_products]
            duplicates = [x for x in set(orders) if orders.count(x) > 1]
            
            if duplicates:
                # Переназначаем order последовательно
                for i, product in enumerate(section_products, 1):
                    old_order = product.get('order', 0)
                    product['order'] = i
                    if old_order != i:
                        fixed_count += 1
        
        if fixed_count > 0:
            print(f"Исправлено {fixed_count} дублей в order")
        
        return fixed_count
    
    def filter_products(self, event=None):
        """Фильтрация товаров по секции"""
        self.refresh_products_list()
    
    def refresh_products_list(self):
        """Обновление списка товаров"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Фильтруем по секции
        section_filter = self.section_var.get()
        filtered_products = self.products
        if section_filter != "all":
            filtered_products = [p for p in self.products if p.get('section') == section_filter]
        
        # Сортируем по order
        filtered_products.sort(key=lambda x: (x.get('section', ''), x.get('order', 0)))
        
        for product in filtered_products:
            # Подсчитываем количество изображений
            image_count = len(product.get("images", "").split("|")) if product.get("images") else 0
            
            self.products_tree.insert("", "end", values=(
                product.get("order", ""),
                product.get("section", ""),
                product.get("title", ""),
                product.get("price", ""),
                product.get("status", ""),
                f"{image_count} фото"
            ))
    
    def on_product_select(self, event):
        """Обработка выбора товара"""
        selection = self.products_tree.selection()
        if not selection:
            return
        
        item = self.products_tree.item(selection[0])
        order = item['values'][0]
        section = item['values'][1]
        title = item['values'][2]
        
        # Находим товар
        product = next((p for p in self.products 
                       if p.get('order') == order and p.get('section') == section 
                       and p.get('title') == title), None)
        if not product:
            return
        
        # Заполняем поля редактирования
        self.edit_title_entry.delete(0, tk.END)
        self.edit_title_entry.insert(0, product.get('title', ''))
        
        self.edit_price_entry.delete(0, tk.END)
        self.edit_price_entry.insert(0, product.get('price', ''))
        
        self.edit_desc_entry.delete(0, tk.END)
        self.edit_desc_entry.insert(0, product.get('desc', ''))
        
        self.edit_meta_entry.delete(0, tk.END)
        self.edit_meta_entry.insert(0, product.get('meta', ''))
        
        self.edit_section_var.set(product.get('section', 'home'))
        self.edit_status_var.set(product.get('status', 'stock'))
        
        # Сохраняем текущий товар для редактирования
        self.current_editing_product = product
        
        # Показываем изображения
        self.show_product_images(product)
    
    def show_product_images(self, product):
        """Показ изображений товара"""
        # Очищаем canvas
        self.canvas.delete("all")
        
        if not product.get('images'):
            return
        
        images = product['images'].split('|')
        x_offset = 10
        
        for i, img_name in enumerate(images):
            # Ищем файл изображения
            img_path = None
            if '/' in img_name:
                # Полный путь
                img_path = os.path.join('img', img_name)
            else:
                # Ищем в папке товара
                folder = product.get('folder', '')
                if folder:
                    img_path = os.path.join(folder, img_name)
                else:
                    # Ищем по всему img
                    for root, dirs, files in os.walk('img'):
                        if img_name in files:
                            img_path = os.path.join(root, img_name)
                            break
            
            if img_path and os.path.exists(img_path):
                try:
                    # Загружаем и масштабируем изображение
                    img = Image.open(img_path)
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Создаем фрейм для изображения
                    img_frame = tk.Frame(self.canvas, bg='white', relief=tk.RAISED, bd=2)
                    self.canvas.create_window(x_offset, 10, anchor=tk.NW, window=img_frame)
                    
                    # Добавляем изображение
                    img_label = tk.Label(img_frame, image=photo, bg='white')
                    img_label.image = photo  # Сохраняем ссылку
                    img_label.pack(padx=5, pady=5)
                    
                    # Добавляем номер
                    num_label = tk.Label(img_frame, text=f"{i+1}", bg='white', 
                                       font=('Arial', 12, 'bold'), fg='blue')
                    num_label.pack(pady=2)
                    
                    x_offset += 170
                    
                except Exception as e:
                    print(f"Ошибка загрузки изображения {img_path}: {e}")
            else:
                # Показываем заглушку для отсутствующего изображения
                placeholder_frame = tk.Frame(self.canvas, bg='lightgray', relief=tk.RAISED, bd=2)
                self.canvas.create_window(x_offset, 10, anchor=tk.NW, window=placeholder_frame)
                
                placeholder_label = tk.Label(placeholder_frame, text=f"❌\n{img_name}", 
                                           bg='lightgray', font=('Arial', 8), 
                                           width=15, height=8)
                placeholder_label.pack(padx=5, pady=5)
                
                x_offset += 170
        
        # Обновляем scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def save_product_changes(self):
        """Сохранение изменений в товаре"""
        if not hasattr(self, 'current_editing_product') or not self.current_editing_product:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования!")
            return
        
        # Получаем новые значения
        new_title = self.edit_title_entry.get().strip()
        new_price = self.edit_price_entry.get().strip()
        new_desc = self.edit_desc_entry.get().strip()
        new_meta = self.edit_meta_entry.get().strip()
        new_section = self.edit_section_var.get()
        new_status = self.edit_status_var.get()
        
        if not new_title:
            messagebox.showerror("Ошибка", "Название товара не может быть пустым!")
            return
        
        # Обновляем товар
        self.current_editing_product['title'] = new_title
        self.current_editing_product['price'] = new_price
        self.current_editing_product['desc'] = new_desc
        self.current_editing_product['meta'] = new_meta
        self.current_editing_product['section'] = new_section
        self.current_editing_product['status'] = new_status
        
        # Сохраняем в файл
        self.save_products()
        
        # Обновляем список
        self.refresh_products_list()
        
        messagebox.showinfo("Успех", f"✅ Товар '{new_title}' обновлен!")
    
    def move_product_up(self):
        """Перемещение товара вверх"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        order = item['values'][0]
        section = item['values'][1]
        title = item['values'][2]
        
        # Находим товар
        product = next((p for p in self.products 
                       if p.get('order') == order and p.get('section') == section 
                       and p.get('title') == title), None)
        if not product:
            return
        
        # Находим предыдущий товар в той же секции
        section_products = [p for p in self.products if p.get('section') == section]
        section_products.sort(key=lambda x: x.get('order', 0))
        
        current_index = None
        for i, p in enumerate(section_products):
            if p.get('id') == product.get('id'):
                current_index = i
                break
        
        if current_index is None or current_index == 0:
            messagebox.showinfo("Информация", "Товар уже в начале списка!")
            return
        
        # Меняем местами order
        prev_product = section_products[current_index - 1]
        product['order'], prev_product['order'] = prev_product['order'], product['order']
        
        # Сохраняем
        self.save_products()
        self.refresh_products_list()
        
        messagebox.showinfo("Успех", f"✅ Товар '{title}' перемещен вверх!")
    
    def move_product_down(self):
        """Перемещение товара вниз"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        order = item['values'][0]
        section = item['values'][1]
        title = item['values'][2]
        
        # Находим товар
        product = next((p for p in self.products 
                       if p.get('order') == order and p.get('section') == section 
                       and p.get('title') == title), None)
        if not product:
            return
        
        # Находим следующий товар в той же секции
        section_products = [p for p in self.products if p.get('section') == section]
        section_products.sort(key=lambda x: x.get('order', 0))
        
        current_index = None
        for i, p in enumerate(section_products):
            if p.get('id') == product.get('id'):
                current_index = i
                break
        
        if current_index is None or current_index == len(section_products) - 1:
            messagebox.showinfo("Информация", "Товар уже в конце списка!")
            return
        
        # Меняем местами order
        next_product = section_products[current_index + 1]
        product['order'], next_product['order'] = next_product['order'], product['order']
        
        # Сохраняем
        self.save_products()
        self.refresh_products_list()
        
        messagebox.showinfo("Успех", f"✅ Товар '{title}' перемещен вниз!")
    
    def delete_product(self):
        """Удаление товара"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][2]
        
        if messagebox.askyesno("Подтверждение", f"Удалить товар '{title}'?"):
            # Находим и удаляем товар
            product = next((p for p in self.products 
                           if p.get('title') == title), None)
            if product:
                # Сохраняем order и section для сдвига
                deleted_order = product.get('order', 0)
                section = product.get('section')
                
                # Удаляем папку с файлами
                if os.path.exists(product.get('folder', '')):
                    shutil.rmtree(product.get('folder'))
                
                # Удаляем из списка
                self.products.remove(product)
                
                # Сдвигаем order на -1 для товаров с большим order
                self.shift_orders_down(section, deleted_order)
                
                # Исправляем дубли в order для раздела
                self.fix_duplicate_orders(section)
                
                self.save_products()
                self.refresh_products_list()
                
                messagebox.showinfo("Успех", f"Товар '{title}' удален!")
    
    def edit_product(self):
        """Редактирование товара (переключение на вкладку редактирования)"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        # Просто показываем информацию в правой панели
        # (функциональность уже есть в on_product_select)
        pass
    
    def clean_filename(self, name):
        """Очистка имени файла для английского названия"""
        # Удаляем все символы кроме букв, цифр и пробелов
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        # Заменяем пробелы на дефисы
        clean = re.sub(r'\s+', '-', clean.strip())
        return clean.lower()
    
    def select_images(self):
        """Выбор изображений"""
        files = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if files:
            self.selected_images.extend(files)
            self.update_images_list()
    
    def update_images_list(self):
        """Обновление списка изображений"""
        self.images_listbox.delete(0, tk.END)
        for i, img_path in enumerate(self.selected_images, 1):
            filename = os.path.basename(img_path)
            self.images_listbox.insert(tk.END, f"{i}. {filename}")
    
    def move_image_up(self):
        """Перемещение изображения вверх"""
        selection = self.images_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            self.selected_images[idx], self.selected_images[idx-1] = \
                self.selected_images[idx-1], self.selected_images[idx]
            self.update_images_list()
            self.images_listbox.selection_set(idx-1)
    
    def move_image_down(self):
        """Перемещение изображения вниз"""
        selection = self.images_listbox.curselection()
        if selection and selection[0] < len(self.selected_images) - 1:
            idx = selection[0]
            self.selected_images[idx], self.selected_images[idx+1] = \
                self.selected_images[idx+1], self.selected_images[idx]
            self.update_images_list()
            self.images_listbox.selection_set(idx+1)
    
    def remove_image(self):
        """Удаление изображения"""
        selection = self.images_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.selected_images[idx]
            self.update_images_list()
    
    def compress_image(self, input_path, output_path, max_size=2000, quality=85):
        """Сжатие изображения"""
        try:
            with Image.open(input_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Изменяем размер если нужно
                if img.width > max_size or img.height > max_size:
                    ratio = min(max_size / img.width, max_size / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Сохраняем сжатое изображение
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                return True
        except Exception as e:
            print(f"Ошибка сжатия {input_path}: {e}")
            return False
    
    def save_product(self):
        """Сохранение товара"""
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        price = self.price_entry.get().strip()
        meta = self.meta_entry.get().strip()
        section = self.section_entry_var.get()
        status = self.status_entry_var.get()
        
        if not title:
            messagebox.showerror("Ошибка", "Введите название товара!")
            return
        
        if not self.selected_images:
            messagebox.showerror("Ошибка", "Выберите хотя бы одно изображение!")
            return
        
        # Показываем индикатор загрузки
        self.save_btn.config(state='disabled', text="💾 Сохранение...")
        self.root.update()
        
        # Запускаем сохранение в отдельном потоке
        import threading
        thread = threading.Thread(target=self._save_product_worker, 
                                args=(title, desc, price, meta, section, status))
        thread.daemon = True
        thread.start()
    
    def _save_product_worker(self, title, desc, price, meta, section, status):
        """Рабочий поток для сохранения товара"""
        try:
            # Получаем следующий ID и order
            next_id = self.get_next_id()
            next_order = self.get_next_order(section)
            
            # Сдвигаем все существующие order на +1
            self.shift_orders_up(section)
            
            # Создаем папку для товара
            clean_name = self.clean_filename(title)
            product_folder = os.path.join("img", f"product_{next_id}")
            os.makedirs(product_folder, exist_ok=True)
            
            # Сжимаем и сохраняем изображения
            image_names = []
            for i, img_path in enumerate(self.selected_images, 1):
                filename = f"product_{next_id}_{i}.jpg"
                output_path = os.path.join(product_folder, filename)
                
                if self.compress_image(img_path, output_path):
                    image_names.append(filename)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", 
                                    f"Не удалось обработать изображение: {img_path}"))
                    return
            
            # Создаем товар
            product = {
                "id": next_id,
                "order": next_order,
                "section": section,
                "title": title,
                "price": price,
                "desc": desc,
                "meta": meta,
                "status": status,
                "images": "|".join(image_names),
                "link": "https://t.me/stub123",
                "created": datetime.now().isoformat()
            }
            
            # Добавляем в список
            self.products.append(product)
            
            # Исправляем дубли в order для раздела
            self.fix_duplicate_orders(section)
            
            self.save_products()
            
            # Обновляем UI в главном потоке
            self.root.after(0, self._save_product_success, title, product_folder, next_id, next_order, len(image_names))
            
        except Exception as e:
            error_msg = f"Ошибка сохранения: {e}"
            self.root.after(0, self._save_product_error, error_msg)
    
    def _save_product_success(self, title, product_folder, next_id, next_order, image_count):
        """Успешное сохранение товара"""
        self.save_btn.config(state='normal', text="💾 Сохранить товар")
        self.refresh_products_list()
        self.clear_form()
        
        messagebox.showinfo("Успех", 
                          f"✅ Товар '{title}' сохранен!\n"
                          f"📁 Папка: {product_folder}\n"
                          f"🆔 ID: {next_id}\n"
                          f"📊 Порядок: {next_order}\n"
                          f"📸 Изображений: {image_count}")
    
    def _save_product_error(self, error_msg):
        """Ошибка сохранения товара"""
        self.save_btn.config(state='normal', text="💾 Сохранить товар")
        messagebox.showerror("Ошибка", error_msg)
        

    
    def clear_form(self):
        """Очистка формы"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.meta_entry.delete(0, tk.END)
        self.section_entry_var.set("home")
        self.status_entry_var.set("stock")
        self.selected_images.clear()
        self.update_images_list()
    
    def paste_text(self, event):
        """Вставка текста из буфера обмена"""
        try:
            clipboard_text = self.root.clipboard_get()
            widget = event.widget
            widget.delete(0, tk.END)
            widget.insert(0, clipboard_text)
            return 'break'  # Предотвращаем стандартную обработку
        except:
            pass  # Игнорируем ошибки
    
    def setup_deploy_tab(self, parent):
        """Настройка вкладки деплоя"""
        # Центрируем содержимое
        center_frame = ttk.Frame(parent)
        center_frame.pack(expand=True, fill=tk.BOTH)
        
        # Заголовок
        title_label = ttk.Label(center_frame, text="🚀 Деплой на GitHub", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Описание
        desc_label = ttk.Label(center_frame, 
                              text="Отправляет изменения на GitHub и запускает деплой сайта", 
                              font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Кнопка деплоя
        self.deploy_btn = ttk.Button(center_frame, text="🚀 Задеплоить на GitHub", 
                                    command=self.deploy_to_github, width=30)
        self.deploy_btn.pack(pady=20)
        
        # Индикатор загрузки
        self.deploy_progress = ttk.Progressbar(center_frame, mode='indeterminate', length=300)
        self.deploy_progress.pack(pady=10)
        
        # Статус деплоя
        self.deploy_status = ttk.Label(center_frame, text="", font=('Arial', 10))
        self.deploy_status.pack(pady=10)
        
        # Лог деплоя
        self.deploy_log = scrolledtext.ScrolledText(center_frame, height=10, width=60)
        self.deploy_log.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    def deploy_to_github(self):
        """Деплой на GitHub"""
        self.deploy_btn.config(state='disabled')
        self.deploy_progress.start()
        self.deploy_status.config(text="🔄 Деплой запущен...")
        self.deploy_log.delete(1.0, tk.END)
        self.deploy_log.insert(tk.END, "🚀 Начинаем деплой...\n")
        
        # Запускаем деплой в отдельном потоке
        import threading
        thread = threading.Thread(target=self._deploy_worker)
        thread.daemon = True
        thread.start()
    
    def _deploy_worker(self):
        """Рабочий поток для деплоя"""
        try:
            import subprocess
            import os
            
            # Проверяем статус Git
            self.deploy_log.insert(tk.END, "📊 Проверяем статус Git...\n")
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.stdout.strip():
                self.deploy_log.insert(tk.END, "📝 Обнаружены изменения, добавляем в Git...\n")
                # Добавляем все изменения
                subprocess.run(['git', 'add', '.'], check=True)
                
                # Коммитим
                commit_msg = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                self.deploy_log.insert(tk.END, f"✅ Коммит создан: {commit_msg}\n")
            else:
                self.deploy_log.insert(tk.END, "✅ Нет изменений для коммита\n")
            
            # Пушим изменения
            self.deploy_log.insert(tk.END, "📤 Отправляем на GitHub...\n")
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            self.deploy_log.insert(tk.END, "✅ Изменения отправлены на GitHub!\n")
            
            # Обновляем UI в главном потоке
            self.root.after(0, self._deploy_success)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Ошибка деплоя: {e}\n"
            self.deploy_log.insert(tk.END, error_msg)
            self.root.after(0, self._deploy_error, error_msg)
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка: {e}\n"
            self.deploy_log.insert(tk.END, error_msg)
            self.root.after(0, self._deploy_error, error_msg)
    
    def _deploy_success(self):
        """Успешный деплой"""
        self.deploy_progress.stop()
        self.deploy_btn.config(state='normal')
        self.deploy_status.config(text="✅ Деплой успешно завершен!")
        self.deploy_log.insert(tk.END, "\n🎉 Деплой завершен!\n")
        self.deploy_log.insert(tk.END, "🌐 Сайт будет обновлен через 1-2 минуты\n")
        self.deploy_log.insert(tk.END, "📊 Статус: https://github.com/nothingitto-ops/platforma-site-clean/actions\n")
        self.deploy_log.insert(tk.END, "🌐 Сайт: https://platformasluchay.ru\n")
    
    def _deploy_error(self, error_msg):
        """Ошибка деплоя"""
        self.deploy_progress.stop()
        self.deploy_btn.config(state='normal')
        self.deploy_status.config(text="❌ Ошибка деплоя")
        self.deploy_log.insert(tk.END, f"\n❌ Деплой не удался: {error_msg}\n")

def main():
    root = tk.Tk()
    app = CleanCatalogManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
