#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Random Password Generator - Генератор случайных паролей
Author: Каюмов Марсель
Version: 1.0.0
Description: Приложение для генерации безопасных паролей с настройками параметров
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import string
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import unittest


class PasswordHistory:
    """Класс для управления историей паролей"""
    
    def __init__(self, filename: str = "password_history.json"):
        self.filename = filename
        self.history: List[Dict] = []
        self.load_history()
    
    def save_history(self) -> bool:
        """Сохранить историю в JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load_history(self) -> bool:
        """Загрузить историю из JSON файла"""
        if not os.path.exists(self.filename):
            return True
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    def add_password(self, password: str, length: int, settings: Dict) -> bool:
        """Добавить пароль в историю"""
        try:
            entry = {
                "id": len(self.history) + 1,
                "password": password,
                "length": length,
                "settings": settings,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.history.insert(0, entry)  # Новые записи в начало
            # Ограничим историю 100 записями
            if len(self.history) > 100:
                self.history = self.history[:100]
            self.save_history()
            return True
        except Exception as e:
            print(f"Ошибка добавления: {e}")
            return False
    
    def clear_history(self) -> bool:
        """Очистить историю"""
        self.history = []
        return self.save_history()
    
    def get_history(self) -> List[Dict]:
        """Получить всю историю"""
        return self.history.copy()


class PasswordGenerator:
    """Класс для генерации паролей"""
    
    def __init__(self):
        self.letters_lower = string.ascii_lowercase
        self.letters_upper = string.ascii_uppercase
        self.digits = string.digits
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def generate(self, length: int, use_uppercase: bool, use_lowercase: bool, 
                 use_digits: bool, use_special: bool) -> str:
        """
        Генерация пароля на основе параметров
        
        Args:
            length: длина пароля
            use_uppercase: использовать заглавные буквы
            use_lowercase: использовать строчные буквы
            use_digits: использовать цифры
            use_special: использовать спецсимволы
        
        Returns:
            сгенерированный пароль
        """
        if length < 4:
            raise ValueError("Минимальная длина пароля - 4 символа")
        if length > 128:
            raise ValueError("Максимальная длина пароля - 128 символов")
        
        charset = ""
        if use_lowercase:
            charset += self.letters_lower
        if use_uppercase:
            charset += self.letters_upper
        if use_digits:
            charset += self.digits
        if use_special:
            charset += self.special_chars
        
        if not charset:
            raise ValueError("Выберите хотя бы один тип символов")
        
        # Генерация пароля
        password = ''.join(random.choice(charset) for _ in range(length))
        
        # Дополнительная проверка: убедимся, что пароль содержит все выбранные типы
        # (для коротких паролей это может быть сложно)
        if length >= 4:
            password = self._ensure_all_types(password, charset, use_uppercase, 
                                              use_lowercase, use_digits, use_special)
        
        return password
    
    def _ensure_all_types(self, password: str, charset: str, use_uppercase: bool,
                          use_lowercase: bool, use_digits: bool, use_special: bool) -> str:
        """Гарантирует, что пароль содержит все выбранные типы символов"""
        password_list = list(password)
        types_to_check = []
        
        if use_uppercase and not any(c in self.letters_upper for c in password):
            types_to_check.append(random.choice(self.letters_upper))
        if use_lowercase and not any(c in self.letters_lower for c in password):
            types_to_check.append(random.choice(self.letters_lower))
        if use_digits and not any(c in self.digits for c in password):
            types_to_check.append(random.choice(self.digits))
        if use_special and not any(c in self.special_chars for c in password):
            types_to_check.append(random.choice(self.special_chars))
        
        # Заменяем первые символы для гарантии
        for i, char in enumerate(types_to_check):
            if i < len(password_list):
                password_list[i] = char
        
        # Перемешиваем результат
        random.shuffle(password_list)
        return ''.join(password_list)
    
    def generate_multiple(self, count: int, length: int, use_uppercase: bool,
                          use_lowercase: bool, use_digits: bool, use_special: bool) -> List[str]:
        """Генерирует несколько паролей"""
        passwords = []
        for _ in range(min(count, 10)):  # Ограничим 10 паролями за раз
            passwords.append(self.generate(length, use_uppercase, use_lowercase,
                                           use_digits, use_special))
        return passwords
    
    def check_strength(self, password: str) -> Dict:
        """Проверка сложности пароля"""
        strength = 0
        feedback = []
        
        if len(password) >= 12:
            strength += 1
            feedback.append("✓ Хорошая длина")
        elif len(password) >= 8:
            feedback.append("⚠ Приемлемая длина")
        else:
            feedback.append("✗ Слишком короткий")
        
        if any(c in string.ascii_lowercase for c in password):
            strength += 1
            feedback.append("✓ Есть строчные буквы")
        else:
            feedback.append("✗ Нет строчных букв")
        
        if any(c in string.ascii_uppercase for c in password):
            strength += 1
            feedback.append("✓ Есть заглавные буквы")
        else:
            feedback.append("✗ Нет заглавных букв")
        
        if any(c in string.digits for c in password):
            strength += 1
            feedback.append("✓ Есть цифры")
        else:
            feedback.append("✗ Нет цифр")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength += 1
            feedback.append("✓ Есть спецсимволы")
        else:
            feedback.append("✗ Нет спецсимволов")
        
        # Оценка сложности
        if strength >= 4:
            level = "Очень сложный"
            color = "green"
        elif strength >= 3:
            level = "Сложный"
            color = "orange"
        elif strength >= 2:
            level = "Средний"
            color = "yellow"
        else:
            level = "Слабый"
            color = "red"
        
        return {
            "level": level,
            "color": color,
            "score": strength,
            "feedback": feedback
        }


class PasswordGeneratorApp:
    """Главное приложение с GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator - Генератор паролей")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Инициализация компонентов
        self.generator = PasswordGenerator()
        self.history = PasswordHistory()
        
        # Настройка внешнего вида
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка истории
        self.refresh_history()
    
    def setup_styles(self):
        """Настройка стилей"""
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4CAF50',
            'button': '#2196F3',
            'button_hover': '#1976D2',
            'error': '#f44336',
            'warning': '#ff9800',
            'success': '#4caf50'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button'])
    
    def create_widgets(self):
        """Создание всех виджетов"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Левая панель - настройки
        self.create_settings_panel(main_frame)
        
        # Правая панель - история
        self.create_history_panel(main_frame)
        
        # Нижняя панель - результат
        self.create_result_panel(main_frame)
    
    def create_settings_panel(self, parent):
        """Панель настроек генерации"""
        settings_frame = ttk.LabelFrame(parent, text="Настройки пароля", padding="15")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Длина пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        length_control_frame = ttk.Frame(settings_frame)
        length_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(length_control_frame, from_=4, to=128, 
                                      orient=tk.HORIZONTAL, variable=self.length_var,
                                      command=self.update_length_label)
        self.length_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.length_label = ttk.Label(length_control_frame, text="12", width=5)
        self.length_label.pack(side=tk.RIGHT)
        
        # Чекбоксы для выбора символов
        ttk.Label(settings_frame, text="Использовать символы:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(settings_frame, text="Строчные буквы (a-z)", 
                       variable=self.use_lowercase).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(settings_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.use_uppercase).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%)", 
                       variable=self.use_special).grid(row=6, column=0, sticky=tk.W, pady=2)
        
        # Кнопки генерации
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.grid(row=7, column=0, pady=(20, 10), sticky=(tk.W, tk.E))
        
        self.generate_btn = tk.Button(btn_frame, text="🔐 Сгенерировать пароль",
                                     bg=self.colors['button'], fg='white',
                                     font=('Arial', 10, 'bold'),
                                     command=self.generate_password, cursor='hand2')
        self.generate_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.generate_5_btn = tk.Button(btn_frame, text="📋 Сгенерировать 5 паролей",
                                       bg=self.colors['accent'], fg='white',
                                       command=self.generate_multiple_passwords, cursor='hand2')
        self.generate_5_btn.pack(fill=tk.X)
        
        # Предустановки
        ttk.Label(settings_frame, text="Быстрые настройки:").grid(row=8, column=0, sticky=tk.W, pady=(15, 5))
        
        presets_frame = ttk.Frame(settings_frame)
        presets_frame.grid(row=9, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(presets_frame, text="Слабый (8 символов)", 
                  command=lambda: self.apply_preset(8, True, False, False, False)).pack(fill=tk.X, pady=2)
        ttk.Button(presets_frame, text="Средний (12 символов)", 
                  command=lambda: self.apply_preset(12, True, True, True, False)).pack(fill=tk.X, pady=2)
        ttk.Button(presets_frame, text="Сильный (16 символов)", 
                  command=lambda: self.apply_preset(16, True, True, True, True)).pack(fill=tk.X, pady=2)
        ttk.Button(presets_frame, text="Максимальный (32 символа)", 
                  command=lambda: self.apply_preset(32, True, True, True, True)).pack(fill=tk.X, pady=2)
    
    def create_history_panel(self, parent):
        """Панель истории паролей"""
        history_frame = ttk.LabelFrame(parent, text="История паролей", padding="10")
        history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview для истории
        tree_frame = ttk.Frame(history_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_tree = ttk.Treeview(tree_frame, 
                                         columns=('id', 'password', 'length', 'date'),
                                         show='headings', yscrollcommand=scrollbar.set, height=15)
        
        self.history_tree.heading('id', text='№')
        self.history_tree.heading('password', text='Пароль')
        self.history_tree.heading('length', text='Длина')
        self.history_tree.heading('date', text='Дата создания')
        
        self.history_tree.column('id', width=40, anchor='center')
        self.history_tree.column('password', width=200)
        self.history_tree.column('length', width=60, anchor='center')
        self.history_tree.column('date', width=140, anchor='center')
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)
        
        # Привязка клика для копирования
        self.history_tree.bind('<Double-Button-1>', self.copy_password_from_history)
        
        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.copy_btn = tk.Button(btn_frame, text="📋 Копировать выбранный",
                                 bg=self.colors['accent'], fg='white',
                                 command=self.copy_selected_password, cursor='hand2')
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = tk.Button(btn_frame, text="🗑 Очистить историю",
                                  bg=self.colors['error'], fg='white',
                                  command=self.clear_history, cursor='hand2')
        self.clear_btn.pack(side=tk.LEFT)
        
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def create_result_panel(self, parent):
        """Панель результатов"""
        result_frame = ttk.LabelFrame(parent, text="Сгенерированный пароль", padding="10")
        result_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Поле для пароля
        self.password_text = scrolledtext.ScrolledText(result_frame, height=3, 
                                                       font=('Courier', 12), wrap=tk.WORD)
        self.password_text.pack(fill=tk.X, pady=(0, 10))
        
        # Индикатор сложности
        strength_frame = ttk.Frame(result_frame)
        strength_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(strength_frame, text="Сложность:").pack(side=tk.LEFT, padx=(0, 10))
        self.strength_label = ttk.Label(strength_frame, text="Не определен", 
                                        foreground=self.colors['warning'])
        self.strength_label.pack(side=tk.LEFT)
        
        # Кнопки действий
        action_frame = ttk.Frame(result_frame)
        action_frame.pack(fill=tk.X)
        
        self.copy_result_btn = tk.Button(action_frame, text="📋 Копировать в буфер",
                                        bg=self.colors['button'], fg='white',
                                        command=self.copy_to_clipboard, cursor='hand2')
        self.copy_result_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = tk.Button(action_frame, text="💾 Сохранить в историю",
                                 bg=self.colors['success'], fg='white',
                                 command=self.save_current_to_history, cursor='hand2')
        self.save_btn.pack(side=tk.LEFT)
        
        result_frame.columnconfigure(0, weight=1)
    
    def update_length_label(self, *args):
        """Обновление метки длины пароля"""
        self.length_label.config(text=str(self.length_var.get()))
    
    def apply_preset(self, length, use_lower, use_upper, use_digits, use_special):
        """Применение предустановки"""
        self.length_var.set(length)
        self.use_lowercase.set(use_lower)
        self.use_uppercase.set(use_upper)
        self.use_digits.set(use_digits)
        self.use_special.set(use_special)
        self.generate_password()
    
    def generate_password(self):
        """Генерация одного пароля"""
        try:
            length = self.length_var.get()
            
            # Валидация
            if length < 4:
                messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
                return
            if length > 128:
                messagebox.showerror("Ошибка", "Максимальная длина пароля - 128 символов")
                return
            
            if not (self.use_lowercase.get() or self.use_uppercase.get() or 
                   self.use_digits.get() or self.use_special.get()):
                messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
                return
            
            # Генерация пароля
            password = self.generator.generate(
                length, self.use_uppercase.get(), self.use_lowercase.get(),
                self.use_digits.get(), self.use_special.get()
            )
            
            # Отображение
            self.password_text.delete("1.0", tk.END)
            self.password_text.insert("1.0", password)
            
            # Проверка сложности
            strength = self.generator.check_strength(password)
            self.strength_label.config(text=strength['level'], foreground=strength['color'])
            
            # Сохраняем текущий пароль для возможного сохранения
            self.current_password = password
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать пароль: {e}")
    
    def generate_multiple_passwords(self):
        """Генерация нескольких паролей"""
        try:
            length = self.length_var.get()
            
            passwords = self.generator.generate_multiple(
                5, length, self.use_uppercase.get(), self.use_lowercase.get(),
                self.use_digits.get(), self.use_special.get()
            )
            
            # Показываем в отдельном окне
            self.show_multiple_passwords(passwords)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def show_multiple_passwords(self, passwords: List[str]):
        """Отображение нескольких паролей в отдельном окне"""
        win = tk.Toplevel(self.root)
        win.title("Сгенерированные пароли")
        win.geometry("500x400")
        
        frame = ttk.Frame(win, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(frame, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        for i, pwd in enumerate(passwords, 1):
            text.insert(tk.END, f"{i}. {pwd}\n")
            text.insert(tk.END, "=" * 50 + "\n")
        
        text.config(state=tk.DISABLED)
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_text.get("1.0", tk.END).strip()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль")
    
    def save_current_to_history(self):
        """Сохранение текущего пароля в историю"""
        password = self.password_text.get("1.0", tk.END).strip()
        if not password:
            messagebox.showwarning("Предупреждение", "Нет пароля для сохранения")
            return
        
        settings = {
            "length": self.length_var.get(),
            "use_uppercase": self.use_uppercase.get(),
            "use_lowercase": self.use_lowercase.get(),
            "use_digits": self.use_digits.get(),
            "use_special": self.use_special.get()
        }
        
        if self.history.add_password(password, len(password), settings):
            messagebox.showinfo("Успех", "Пароль сохранен в историю!")
            self.refresh_history()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить пароль")
    
    def copy_selected_password(self):
        """Копирование выбранного из истории"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль из истории")
            return
        
        password = self.history_tree.item(selected[0])['values'][1]
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
    
    def copy_password_from_history(self, event):
        """Копирование по двойному клику"""
        self.copy_selected_password()
    
    def refresh_history(self):
        """Обновление списка истории"""
        # Очистка Treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей
        for entry in self.history.get_history():
            self.history_tree.insert('', 'end', values=(
                entry['id'], entry['password'][:30] + ('...' if len(entry['password']) > 30 else ''),
                entry['length'], entry['created_at']
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            if self.history.clear_history():
                messagebox.showinfo("Успех", "История очищена")
                self.refresh_history()
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить историю")


# Модульные тесты
class TestPasswordGenerator(unittest.TestCase):
    """Тестирование генератора паролей"""
    
    def setUp(self):
        self.generator = PasswordGenerator()
    
    def test_generate_valid_password(self):
        """Позитивный тест: генерация валидного пароля"""
        password = self.generator.generate(12, True, True, True, True)
        self.assertEqual(len(password), 12)
    
    def test_generate_min_length(self):
        """Граничный тест: минимальная длина"""
        password = self.generator.generate(4, True, True, True, True)
        self.assertEqual(len(password), 4)
    
    def test_generate_max_length(self):
        """Граничный тест: максимальная длина"""
        password = self.generator.generate(128, True, True, True, True)
        self.assertEqual(len(password), 128)
    
    def test_length_too_short(self):
        """Негативный тест: слишком короткий пароль"""
        with self.assertRaises(ValueError):
            self.generator.generate(3, True, True, True, True)
    
    def test_length_too_long(self):
        """Негативный тест: слишком длинный пароль"""
        with self.assertRaises(ValueError):
            self.generator.generate(129, True, True, True, True)
    
    def test_no_characters_selected(self):
        """Негативный тест: не выбрано ни одного типа символов"""
        with self.assertRaises(ValueError):
            self.generator.generate(12, False, False, False, False)
    
    def test_only_lowercase(self):
        """Позитивный тест: только строчные буквы"""
        password = self.generator.generate(20, False, True, False, False)
        self.assertTrue(all(c.islower() for c in password))
    
    def test_only_uppercase(self):
        """Позитивный тест: только заглавные буквы"""
        password = self.generator.generate(20, True, False, False, False)
        self.assertTrue(all(c.isupper() for c in password))
    
    def test_only_digits(self):
        """Позитивный тест: только цифры"""
        password = self.generator.generate(20, False, False, True, False)
        self.assertTrue(all(c.isdigit() for c in password))
    
    def test_check_strength(self):
        """Позитивный тест: проверка сложности"""
        strength = self.generator.check_strength("StrongP@ssw0rd123!")
        self.assertIn('level', strength)
        self.assertIn('score', strength)
    
    def test_generate_multiple(self):
        """Позитивный тест: генерация нескольких паролей"""
        passwords = self.generator.generate_multiple(5, 12, True, True, True, True)
        self.assertEqual(len(passwords), 5)
        self.assertTrue(all(len(p) == 12 for p in passwords))


class TestPasswordHistory(unittest.TestCase):
    """Тестирование истории паролей"""
    
    def setUp(self):
        self.test_file = "test_history.json"
        self.history = PasswordHistory(self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_add_password(self):
        """Позитивный тест: добавление пароля"""
        settings = {"length": 12}
        result = self.history.add_password("TestPass123", 12, settings)
        self.assertTrue(result)
        self.assertEqual(len(self.history.get_history()), 1)
    
    def test_clear_history(self):
        """Позитивный тест: очистка истории"""
        settings = {"length": 12}
        self.history.add_password("TestPass123", 12, settings)
        self.history.clear_history()
        self.assertEqual(len(self.history.get_history()), 0)


def run_tests():
    """Запуск всех тестов"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPasswordGenerator)
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordHistory))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def main():
    """Главная функция"""
    print("=" * 60)
    print("Random Password Generator v1.0.0")
    print("Автор: Иван Иванов")
    print("=" * 60)
    
    # Запуск тестов
    choice = input("\nЗапустить тесты перед стартом? (y/n): ").lower()
    if choice == 'y':
        print("\nЗапуск тестов...")
        if run_tests():
            print("✅ Все тесты пройдены успешно!\n")
        else:
            print("❌ Некоторые тесты не пройдены")
            if input("Продолжить? (y/n): ").lower() != 'y':
                return
    
    # Запуск GUI
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
