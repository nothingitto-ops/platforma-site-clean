#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import shutil
from PIL import Image, ImageTk
import zipfile
from datetime import datetime
import re
import requests
import csv
import io

class ImprovedCatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛍️ Catalog Manager Pro")
        self.root.geometry("1200x800")
        
        # Настройка стилей для кнопок
        self.setup_styles()
        
        # Данные
        self.products = []
        self.selected_images = []
        self.sheets_data = []
        self.load_products()
        # self.load_sheets_data()  # Временно отключено
        
        self.setup_ui()
    
    def setup_styles(self):
        """Настройка стилей для кнопок"""
        style = ttk.Style()
        
        # Увеличиваем размер шрифта для кнопок
        style.configure('TButton', font=('Arial', 12))
        
        # Создаем стиль для больших кнопок
        style.configure('Large.TButton', font=('Arial', 13, 'bold'), padding=5)
        
        # Создаем стиль для кнопок действий
        style.configure('Action.TButton', font=('Arial', 12), padding=3)
        
        # Стили для Treeview (список товаров)
        style.configure('Treeview', font=('Arial', 12), rowheight=30)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))
        
        # Стили для текстовых полей
        style.configure('TEntry', font=('Arial', 12))
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TLabelframe.Label', font=('Arial', 12, 'bold'))
        
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
        
        # Вкладка 3: Экспорт
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="📤 Экспорт")
        self.setup_export_tab(export_frame)
        
    def setup_products_tab(self, parent):
        """Настройка вкладки с товарами"""
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопки управления
        sync_btn = ttk.Button(top_frame, text="🔄 Синхронизировать с Google Sheets", 
                             command=self.sync_google_sheets, width=35)
        sync_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        deploy_btn = ttk.Button(top_frame, text="🚀 Деплой на GitHub", 
                               command=self.deploy_to_github, width=20)
        deploy_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Основной контейнер
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Левая панель - список товаров
        left_frame = ttk.LabelFrame(main_frame, text="📋 Список товаров", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Список товаров
        self.products_tree = ttk.Treeview(left_frame, columns=("title", "price", "images"), show="headings", height=20)
        self.products_tree.heading("title", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("images", text="Фото")
        self.products_tree.column("title", width=300)
        self.products_tree.column("price", width=100)
        self.products_tree.column("images", width=80)
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления товарами
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # Создаем кнопки с увеличенными размерами и стилями
        copy_btn = ttk.Button(btn_frame, text="📋 Копировать имена", 
                             command=self.copy_image_names, width=20, style='Action.TButton')
        copy_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        reorder_btn = ttk.Button(btn_frame, text="🖼️ Изменить порядок фото", 
                                command=self.reorder_images, width=20, style='Action.TButton')
        reorder_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        edit_btn = ttk.Button(btn_frame, text="✏️ Редактировать", 
                             command=self.edit_product, width=20, style='Action.TButton')
        edit_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        delete_btn = ttk.Button(btn_frame, text="🗑️ Удалить", 
                               command=self.delete_product, width=20, style='Action.TButton')
        delete_btn.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        
        # Правая панель - просмотр товара
        right_frame = ttk.LabelFrame(main_frame, text="👁️ Просмотр товара", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Информация о товаре
        info_frame = ttk.LabelFrame(right_frame, text="📝 Информация о товаре", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Поля для редактирования
        ttk.Label(info_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.edit_title_entry = ttk.Entry(info_frame, width=30, font=('Arial', 12))
        self.edit_title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Цена:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.edit_price_entry = ttk.Entry(info_frame, width=30, font=('Arial', 12))
        self.edit_price_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.edit_desc_entry = ttk.Entry(info_frame, width=30, font=('Arial', 12))
        self.edit_desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(info_frame, text="Мета:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.edit_meta_entry = ttk.Entry(info_frame, width=30, font=('Arial', 12))
        self.edit_meta_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        # Кнопка сохранения изменений
        save_changes_btn = ttk.Button(info_frame, text="💾 Сохранить изменения", 
                                     command=self.save_product_changes, style='Action.TButton')
        save_changes_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
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
        
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_entry = ttk.Entry(form_frame, width=50)
        self.desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_entry = ttk.Entry(form_frame, width=50)
        self.price_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(form_frame, text="Мета:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.meta_entry = ttk.Entry(form_frame, width=50)
        self.meta_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        # Настройка весов
        form_frame.columnconfigure(1, weight=1)
        
        # Панель изображений
        images_frame = ttk.LabelFrame(parent, text="📸 Изображения", padding="10")
        images_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Кнопки изображений
        img_btn_frame = ttk.Frame(images_frame)
        img_btn_frame.pack(fill=tk.X, pady=5)
        
        select_btn = ttk.Button(img_btn_frame, text="📸 Выбрать фото", 
                               command=self.select_images, width=15)
        select_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        up_btn = ttk.Button(img_btn_frame, text="⬆️", command=self.move_image_up, width=5)
        up_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        down_btn = ttk.Button(img_btn_frame, text="⬇️", command=self.move_image_down, width=5)
        down_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        remove_btn = ttk.Button(img_btn_frame, text="❌", command=self.remove_image, width=5)
        remove_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Список выбранных изображений
        self.images_listbox = tk.Listbox(images_frame, height=8)
        self.images_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопка сохранения
        save_btn = ttk.Button(parent, text="💾 Сохранить товар", 
                             command=self.save_product, width=25)
        save_btn.pack(pady=10)
        
    def setup_export_tab(self, parent):
        """Настройка вкладки экспорта"""
        # Центрируем содержимое
        center_frame = ttk.Frame(parent)
        center_frame.pack(expand=True, fill=tk.BOTH)
        
        # Заголовок
        title_label = ttk.Label(center_frame, text="🚀 Создание архива для деплоя", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Описание
        desc_label = ttk.Label(center_frame, 
                              text="Создает ZIP архив со всеми файлами сайта,\nготовый для загрузки на Netlify", 
                              font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Кнопка создания архива
        archive_btn = ttk.Button(center_frame, text="📦 Создать архив для деплоя", 
                                command=self.create_deploy_archive, width=30, style='Large.TButton')
        archive_btn.pack(pady=20)
    
    def load_sheets_data(self):
        """Загрузка данных из Google Sheets"""
        try:
            if os.path.exists('sheets_data.json'):
                with open('sheets_data.json', 'r', encoding='utf-8') as f:
                    self.sheets_data = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки данных Google Sheets: {e}")
            self.sheets_data = []
    
    def update_from_sheets(self):
        """Обновление данных из Google Sheets"""
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/fetch_sheets_data.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.load_sheets_data()
                self.refresh_products_list()
                messagebox.showinfo("Обновление", "✅ Данные обновлены из Google Sheets!")
            else:
                messagebox.showerror("Ошибка", f"Ошибка обновления:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные:\n{e}")
    
    def sync_with_sheets(self):
        """Синхронизация с Google Sheets"""
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/sync_with_sheets_improved.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                messagebox.showinfo("✅ Синхронизация завершена!", 
                                  f"🎉 Данные синхронизированы!\n\n"
                                  f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
            else:
                messagebox.showerror("Ошибка", f"Ошибка синхронизации:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось синхронизировать:\n{e}")
    

    
    def setup_google_api(self):
        """Настройка Google Sheets API"""
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/setup_google_api.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                messagebox.showinfo("✅ Настройка завершена!", 
                                  "Google Sheets API настроен!\n\n"
                                  "Теперь можно обновлять таблицу автоматически.")
            else:
                messagebox.showerror("Ошибка", f"Ошибка настройки:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось настроить API:\n{e}")
    
    def on_product_select(self, event):
        """Обработка выбора товара"""
        selection = self.products_tree.selection()
        if not selection:
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][0]
        
        product = next((p for p in self.products if p["title"] == title), None)
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
        
        # Сохраняем текущий товар для редактирования
        self.current_editing_product = product
        
        # Показываем изображения
        self.show_product_images(product)
    
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
        
        if not new_title:
            messagebox.showerror("Ошибка", "Название товара не может быть пустым!")
            return
        
        # Обновляем товар
        self.current_editing_product['title'] = new_title
        self.current_editing_product['price'] = new_price
        self.current_editing_product['desc'] = new_desc
        self.current_editing_product['meta'] = new_meta
        
        # Сохраняем в файл
        self.save_products()
        
        # Обновляем список
        self.refresh_products_list()
        
        messagebox.showinfo("Успех", f"✅ Товар '{new_title}' обновлен!")
    
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
                # Только имя файла, ищем в папке товара
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
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
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
                                       font=('Arial', 14, 'bold'), fg='blue')
                    num_label.pack(pady=2)
                    
                    x_offset += 220
                    
                except Exception as e:
                    print(f"Ошибка загрузки изображения {img_path}: {e}")
            else:
                # Показываем заглушку для отсутствующего изображения
                placeholder_frame = tk.Frame(self.canvas, bg='lightgray', relief=tk.RAISED, bd=2)
                self.canvas.create_window(x_offset, 10, anchor=tk.NW, window=placeholder_frame)
                
                placeholder_label = tk.Label(placeholder_frame, text=f"❌\n{img_name}", 
                                           bg='lightgray', font=('Arial', 10), 
                                           width=20, height=10)
                placeholder_label.pack(padx=5, pady=5)
                
                x_offset += 220
        
        # Обновляем scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def refresh_products_list(self):
        """Обновление списка товаров"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for product in self.products:
            # Подсчитываем количество изображений
            image_count = len(product["images"].split("|")) if product["images"] else 0
            
            self.products_tree.insert("", "end", values=(
                product["title"],
                product.get("price", ""),
                f"{image_count} фото"
            ))
    
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
        
        if not title:
            messagebox.showerror("Ошибка", "Введите название товара!")
            return
        
        if not self.selected_images:
            messagebox.showerror("Ошибка", "Выберите хотя бы одно изображение!")
            return
        
        # Создаем папку для товара
        clean_name = self.clean_filename(title)
        product_folder = os.path.join("img", clean_name)
        os.makedirs(product_folder, exist_ok=True)
        
        # Сжимаем и сохраняем изображения
        image_names = []
        for i, img_path in enumerate(self.selected_images, 1):
            filename = f"{clean_name}-{i}.jpg"
            output_path = os.path.join(product_folder, filename)
            
            if self.compress_image(img_path, output_path):
                image_names.append(filename)
            else:
                messagebox.showerror("Ошибка", f"Не удалось обработать изображение: {img_path}")
                return
        
        # Создаем товар
        product = {
            "title": title,
            "desc": desc,
            "price": price,
            "meta": meta,
            "status": "active",
            "images": "|".join(image_names),
            "folder": product_folder,
            "created": datetime.now().isoformat()
        }
        
        # Добавляем в конец списка
        self.products.append(product)
        self.save_products()
        self.refresh_products_list()
        
        # Очищаем форму
        self.clear_form()
        
        messagebox.showinfo("Успех", 
                          f"✅ Товар '{title}' сохранен!\n"
                          f"📁 Папка: {product_folder}\n"
                          f"📸 Изображений: {len(image_names)}")
    
    def clear_form(self):
        """Очистка формы"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.meta_entry.delete(0, tk.END)
        self.selected_images.clear()
        self.update_images_list()
    
    def copy_image_names(self):
        """Копирование имен изображений в буфер"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][0]
        
        product = next((p for p in self.products if p["title"] == title), None)
        if not product or not product["images"]:
            messagebox.showwarning("Предупреждение", "У товара нет изображений!")
            return
        
        # Копируем в буфер
        self.root.clipboard_clear()
        self.root.clipboard_append(product["images"])
        
        messagebox.showinfo("Успех", 
                          f"✅ Имена файлов скопированы!\n\n{product['images']}\n\n"
                          "Теперь можете вставить их в Google Sheets")
    
    def edit_product(self):
        """Редактирование товара"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][0]
        
        product = next((p for p in self.products if p["title"] == title), None)
        if not product:
            return
        
        # Заполняем форму
        self.clear_form()
        self.title_entry.insert(0, product["title"])
        self.desc_entry.insert(0, product.get("desc", ""))
        self.price_entry.insert(0, product.get("price", ""))
        self.meta_entry.insert(0, product.get("meta", ""))
        
        # Загружаем изображения
        if product["images"]:
            image_names = product["images"].split("|")
            for img_name in image_names:
                img_path = os.path.join(product["folder"], img_name)
                if os.path.exists(img_path):
                    self.selected_images.append(img_path)
            self.update_images_list()
        
        # Удаляем старый товар
        self.products.remove(product)
        self.refresh_products_list()
    
    def delete_product(self):
        """Удаление товара"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить товар '{title}'?"):
            product = next((p for p in self.products if p["title"] == title), None)
            if product:
                # Удаляем папку с файлами
                if os.path.exists(product["folder"]):
                    shutil.rmtree(product["folder"])
                
                # Удаляем из списка
                self.products.remove(product)
                self.save_products()
                self.refresh_products_list()
                
                messagebox.showinfo("Успех", f"Товар '{title}' удален!\n\nНажмите '🔄 Синхронизировать' чтобы убрать его из Google Sheets")
    
    def reorder_images(self):
        """Изменение порядка изображений"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар!")
            return
        
        item = self.products_tree.item(selection[0])
        title = item['values'][0]
        
        product = next((p for p in self.products if p["title"] == title), None)
        if not product or not product.get("images"):
            messagebox.showwarning("Предупреждение", "У товара нет изображений!")
            return
        
        # Создаем окно для изменения порядка
        reorder_window = tk.Toplevel(self.root)
        reorder_window.title(f"🖼️ Изменить порядок фото - {title}")
        reorder_window.geometry("600x500")
        
        # Список изображений
        images_frame = ttk.LabelFrame(reorder_window, text="📸 Изображения", padding="10")
        images_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Список изображений
        images_listbox = tk.Listbox(images_frame, height=15)
        images_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Загружаем изображения
        image_names = product["images"].split("|")
        for i, img_name in enumerate(image_names, 1):
            images_listbox.insert(tk.END, f"{i}. {img_name}")
        
        # Кнопки управления
        btn_frame = ttk.Frame(images_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        def move_up():
            selection = images_listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                # Меняем местами в списке
                image_names[idx], image_names[idx-1] = image_names[idx-1], image_names[idx]
                # Обновляем отображение
                images_listbox.delete(0, tk.END)
                for i, img_name in enumerate(image_names, 1):
                    images_listbox.insert(tk.END, f"{i}. {img_name}")
                images_listbox.selection_set(idx-1)
        
        def move_down():
            selection = images_listbox.curselection()
            if selection and selection[0] < len(image_names) - 1:
                idx = selection[0]
                # Меняем местами в списке
                image_names[idx], image_names[idx+1] = image_names[idx+1], image_names[idx]
                # Обновляем отображение
                images_listbox.delete(0, tk.END)
                for i, img_name in enumerate(image_names, 1):
                    images_listbox.insert(tk.END, f"{i}. {img_name}")
                images_listbox.selection_set(idx+1)
        
        def save_order():
            # Обновляем порядок в товаре
            product["images"] = "|".join(image_names)
            self.save_products()
            self.refresh_products_list()
            
            # Обновляем отображение в основном окне
            if hasattr(self, 'product_info'):
                self.on_product_select(None)
            
            messagebox.showinfo("Успех", "✅ Порядок изображений сохранен!")
            reorder_window.destroy()
        
        def copy_new_names():
            # Копируем новые имена в буфер
            new_names = "|".join(image_names)
            self.root.clipboard_clear()
            self.root.clipboard_append(new_names)
            messagebox.showinfo("Копирование", 
                              f"✅ Новые имена файлов скопированы!\n\n{new_names}\n\n"
                              "Теперь можете вставить их в Google Sheets")
        
        up_btn = ttk.Button(btn_frame, text="⬆️", command=move_up, width=5)
        up_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        down_btn = ttk.Button(btn_frame, text="⬇️", command=move_down, width=5)
        down_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        save_btn = ttk.Button(btn_frame, text="💾 Сохранить порядок", 
                             command=save_order, width=20)
        save_btn.pack(side=tk.LEFT, padx=10, pady=2)
        
        copy_btn = ttk.Button(btn_frame, text="📋 Копировать новые имена", 
                             command=copy_new_names, width=25)
        copy_btn.pack(side=tk.LEFT, padx=5, pady=2)
    
    def import_from_folders(self):
        """Импорт товаров из папок"""
        try:
            import subprocess
            result = subprocess.run(['python', 'scripts/import_existing_products.py'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                # Перезагружаем товары
                self.load_products()
                self.refresh_products_list()
                messagebox.showinfo("Импорт", 
                                  f"✅ Импорт завершен!\n"
                                  f"📦 Товаров загружено: {len(self.products)}")
            else:
                messagebox.showerror("Ошибка", f"Ошибка импорта:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить импорт:\n{e}")
    
    def export_to_sheets(self):
        """Экспорт в Google Sheets формат"""
        if not self.products:
            messagebox.showwarning("Предупреждение", "Нет товаров для экспорта!")
            return
        
        # Создаем TSV данные
        tsv_lines = ["Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink"]
        
        for product in self.products:
            # Получаем английское название папки
            folder_name = os.path.basename(product.get('folder', ''))
            if not folder_name:
                folder_name = self.clean_filename(product['title'])
            
            # Формируем имена изображений с английскими названиями
            if product.get('images'):
                image_names = product['images'].split('|')
                english_images = [f"{folder_name}/{img}" for img in image_names]
                images_str = "|".join(english_images)
            else:
                images_str = ""
            
            tsv_line = f"home\t{product['title']}\t{product.get('price', '')}\t{product.get('desc', '')}\t{product.get('meta', '')}\t{product.get('status', 'active')}\t{images_str}\thttps://t.me/stub123"
            tsv_lines.append(tsv_line)
        
        tsv_content = "\n".join(tsv_lines)
        
        # Сохраняем файл
        filename = f"google-sheets-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tsv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tsv_content)
        
        # Копируем в буфер
        self.root.clipboard_clear()
        self.root.clipboard_append(tsv_content)
        
        messagebox.showinfo("Google Sheets", 
                          f"✅ Данные подготовлены для Google Sheets!\n"
                          f"📁 Файл: {filename}\n"
                          f"📋 Данные скопированы в буфер\n\n"
                          f"Инструкция:\n"
                          f"1. Откройте Google Sheets\n"
                          f"2. Вставьте данные из буфера\n"
                          f"3. Сохраните таблицу")
    
    def show_sheets_data(self):
        """Показать данные из Google Sheets"""
        if not self.sheets_data:
            messagebox.showinfo("Информация", "Нет данных из Google Sheets. Нажмите 'Обновить из Google Sheets'")
            return
        
        # Создаем окно с данными
        data_window = tk.Toplevel(self.root)
        data_window.title("📊 Данные Google Sheets")
        data_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(data_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, product in enumerate(self.sheets_data, 1):
            text_widget.insert(tk.END, f"{i}. {product['title']}\n")
            text_widget.insert(tk.END, f"   Цена: {product.get('price', 'Не указана')}\n")
            text_widget.insert(tk.END, f"   Описание: {product.get('desc', 'Не указано')}\n")
            text_widget.insert(tk.END, f"   Изображения: {product.get('images', 'Не указаны')}\n")
            text_widget.insert(tk.END, "-" * 50 + "\n")
    
    def create_deploy_archive(self):
        """Создание архива для деплоя"""
        if not self.products:
            messagebox.showwarning("Предупреждение", "Нет товаров для архива!")
            return
        
        # Создаем архив
        archive_name = f"platforma-site-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Добавляем основные файлы сайта из папки web
            web_files = ['index.html', 'styles.min.css', 'mobile.overrides.css']
            for file in web_files:
                web_path = os.path.join('web', file)
                if os.path.exists(web_path):
                    zipf.write(web_path, file)
                elif os.path.exists(file):
                    zipf.write(file)
            
            # Добавляем папку img со всеми товарами
            if os.path.exists('img'):
                for root, dirs, files in os.walk('img'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, '.')
                        zipf.write(file_path, arc_name)
            
            # Создаем TSV файл для сайта
            tsv_lines = ["Section\tTitle\tPrice\tDesc\tMeta\tStatus\tImages\tLink"]
            
            for product in self.products:
                # Определяем группу товара
                section = "home"  # по умолчанию
                if "nessffo" in product.get('desc', '').lower() or "nessffo" in product.get('title', '').lower():
                    section = "nessffo"
                
                # Получаем правильное название папки
                folder_path = product.get('folder', '')
                if folder_path.startswith('img/'):
                    folder_name = folder_path[4:]  # Убираем 'img/'
                else:
                    folder_name = os.path.basename(folder_path)
                
                if not folder_name:
                    folder_name = self.clean_filename(product['title'])
                
                # Формируем имена изображений с правильными путями
                if product.get('images'):
                    image_names = product['images'].split('|')
                    # Используем полные пути к изображениям от корня сайта
                    full_images = []
                    for img in image_names:
                        # Проверяем, содержит ли имя файла уже путь к папке
                        if '/' in img:
                            # Имя файла уже содержит путь к папке
                            full_images.append(f"img/{img}")
                        else:
                            # Имя файла не содержит путь, добавляем папку
                            if folder_name:
                                full_images.append(f"img/{folder_name}/{img}")
                            else:
                                full_images.append(f"img/{img}")
                    images_str = "|".join(full_images)
                else:
                    images_str = ""
                
                tsv_line = f"{section}\t{product['title']}\t{product.get('price', '')}\t{product.get('desc', '')}\t{product.get('meta', '')}\t{product.get('status', 'active')}\t{images_str}\thttps://t.me/stub123"
                tsv_lines.append(tsv_line)
            
            tsv_content = "\n".join(tsv_lines)
            zipf.writestr('catalog.tsv', tsv_content)
            
            # Создаем обновленный JavaScript файл с локальным TSV
            try:
                with open(os.path.join('web', 'app.min.js'), 'r', encoding='utf-8') as f:
                    js_content = f.read()
                
                # Заменяем URL Google Sheets на локальный TSV файл
                js_content = js_content.replace(
                    "const SHEET_TSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g/pub?output=tsv';",
                    "const SHEET_TSV_URL = './catalog.tsv';"
                )
                
                zipf.writestr('app.min.js', js_content)
            except Exception as e:
                print(f"Ошибка обновления JS файла: {e}")
            
            # Добавляем README с инструкциями
            readme_content = f"""# Platforma Site - Деплой на Netlify

## 📦 Содержимое архива:
- `index.html` - главная страница
- `app.min.js` - логика сайта (обновлена для локального TSV)
- `styles.min.css` - стили
- `mobile.overrides.css` - мобильная версия
- `img/` - папка с изображениями товаров
- `catalog.tsv` - данные каталога ({len(self.products)} товаров)

## 🚀 Деплой на Netlify:

### Вариант 1: Drag & Drop
1. Распакуйте архив
2. Перетащите содержимое папки в Netlify
3. Сайт будет доступен по адресу: https://your-site.netlify.app

### Вариант 2: Git
1. Распакуйте архив
2. Создайте Git репозиторий
3. Загрузите файлы в репозиторий
4. Подключите к Netlify

## 📊 Обновление каталога:
1. Откройте `catalog.tsv` в Google Sheets
2. Внесите изменения
3. Опубликуйте как веб-страницу
4. Скопируйте URL и обновите в `app.min.js`

## ✅ Проверка:
- Все изображения товаров включены
- TSV файл содержит {len(self.products)} товаров
- JavaScript настроен на локальный TSV файл
- Сайт готов к деплою

Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            zipf.writestr('README.md', readme_content)
            
            # Добавляем .gitignore для Netlify
            gitignore_content = """# Netlify
.netlify/
"""
            zipf.writestr('.gitignore', gitignore_content)
        
        messagebox.showinfo("Архив создан", 
                          f"✅ Архив для деплоя создан!\n"
                          f"📦 Файл: {archive_name}\n"
                          f"📊 Товаров: {len(self.products)}\n"
                          f"🖼️ Изображений: {sum(len(p.get('images', '').split('|')) for p in self.products)}\n\n"
                          f"🚀 Готов к загрузке на Netlify!")
    
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

    def sync_google_sheets(self):
        """Универсальная синхронизация с Google Sheets"""
        try:
            import subprocess
            result = subprocess.run(['python', '-c', 
                                   'from auto_update_oauth2 import full_sync_oauth2; full_sync_oauth2()'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                messagebox.showinfo("✅ Синхронизация завершена!", 
                                  f"🎉 Google Sheets полностью синхронизирован!\n\n"
                                  f"📊 Все изменения применены\n"
                                  f"🗑️ Удаленные товары убраны\n"
                                  f"➕ Новые товары добавлены\n"
                                  f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
            else:
                messagebox.showerror("Ошибка", f"Ошибка синхронизации:\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось синхронизировать:\n{e}")

    def deploy_to_github(self):
        """Деплой на GitHub Pages"""
        try:
            import subprocess
            
            # Проверяем статус Git
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.stdout.strip():
                # Есть изменения, предлагаем сохранить
                response = messagebox.askyesno("Изменения обнаружены", 
                                             "Обнаружены несохраненные изменения.\n"
                                             "Хотите сохранить их перед деплоем?")
                if response:
                    # Добавляем все изменения
                    subprocess.run(['git', 'add', '.'], check=True)
                    
                    # Коммитим
                    commit_msg = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                else:
                    messagebox.showinfo("Отменено", "Деплой отменен")
                    return
            
            # Пушим изменения
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            messagebox.showinfo("✅ Деплой запущен!", 
                              f"🚀 Изменения отправлены на GitHub!\n\n"
                              f"📊 Статус деплоя:\n"
                              f"   https://github.com/nothingitto-ops/platforma-site-clean/actions\n\n"
                              f"🌐 Тестовый сервер:\n"
                              f"   https://nothingitto-ops.github.io/platforma-site-clean/\n\n"
                              f"🎯 Основной сайт:\n"
                              f"   https://platformasluchay.ru\n\n"
                              f"⏱️ Деплой обычно занимает 1-2 минуты")
                
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Ошибка деплоя", f"Ошибка Git:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить деплой:\n{e}")

def main():
    root = tk.Tk()
    app = ImprovedCatalogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
