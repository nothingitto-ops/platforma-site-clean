#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Парсим URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Если запрос к корню, отдаем index.html
        if path == '/':
            path = '/index.html'
        
        # Если запрос к API для получения товаров
        if path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                if os.path.exists('products.json'):
                    with open('products.json', 'r', encoding='utf-8') as f:
                        products = json.load(f)
                    self.wfile.write(json.dumps(products, ensure_ascii=False).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps([]).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return
        
        # Для всех остальных файлов используем стандартную обработку
        return super().do_GET()

def main():
    PORT = 8001
    
    # Проверяем, что файлы сайта существуют
    if not os.path.exists('index.html'):
        print("❌ Файл index.html не найден!")
        return
    
    # Проверяем, что products.json существует
    if not os.path.exists('products.json'):
        print("❌ Файл products.json не найден!")
        return
    
    print(f"🚀 Запуск веб-сервера на порту {PORT}")
    print(f"📁 Текущая директория: {os.getcwd()}")
    print(f"🌐 Сайт будет доступен по адресу: http://localhost:{PORT}")
    print("⏹️  Для остановки сервера нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Сервер запущен на http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    main()
