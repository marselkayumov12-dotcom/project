python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note Keeper - Менеджер заметок с фильтрацией и JSON-хранилищем
Author: Иван Иванов
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from unittest.mock import patch
import unittest


@dataclass
class Note:
    """Класс заметки с валидацией"""
    title: str
    content: str
    priority: str  # 'Высокий', 'Средний', 'Низкий'
    category: str
    created_at: str
    note_id: int
    
    def __post_init__(self):
        self.validate()
    
    def validate(self):
        if not self.title or not self.title.strip():
            raise ValueError("Заголовок не может быть пустым")
        if len(self.title) > 100:
            raise ValueError("Заголовок не может превышать 100 символов")
        if len(self.content) > 5000:
            raise ValueError("Содержание не может превышать 5000 символов")
        if self.priority not in ['Высокий', 'Средний', 'Низкий']:
            raise ValueError("Некорректный приоритет")
        if not self.category or not self.category.strip():
            raise ValueError("Категория не может быть пустой")
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Note':
        return cls(**data)


class NoteStorage:
    """Класс для работы с JSON-хранилищем"""
    
    def __init__(self, filename: str = "notes.json"):
        self.filename = filename
        self.notes: List[Note] = []
        self.next_id = 1
        self.load()
    
    def save(self) -> bool:
        """Сохранить заметки в JSON файл"""
        try:
            data = {
                "next_id": self.next_id,
                "notes": [note.to_dict() for note in self.notes]
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load(self) -> bool:
        """Загрузить заметки из JSON файла"""
        if not os.path.exists(self.filename):
            return True
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.next_id = data.get("next_id", 1)
            self.notes = [Note.from_dict(note_data) for note_data in data.get("notes", [])]
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    def add_note(self, note: Note) -> bool:
        """Добавить новую заметку"""
        try:
            note.validate()
            note.note_id = self.next_id
            note.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.notes.append(note)
            self.next_id += 1
            self.save()
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Ошибка добавления заметки: {e}")
    
    def remove_note(self, note_id: int) -> bool:
        """Удалить заметку по ID"""
        initial_len = len(self.notes)
        self.notes = [note for note in self.notes if note.note_id != note_id]
        if len(self.notes) < initial_len:
            self.save()
            return True
        return False
    
    def get_all_notes(self) -> List[Note]:
        return self.notes.copy()
    
    def filter_notes(self, category: Optional[str] = None, 
                     priority: Optional[str] = None,
                     search_text: Optional[str] = None) -> List[Note]:
        """Фильтрация заметок по различным критериям"""
        result = self.notes.copy()
        
        if category and category != "Все":
            result = [n for n in result if n.category == category]
        
        if priority and priority != "Все":
            result = [n for n in result if n.priority == priority]
        
        if search_text and search_text.strip():
            search_lower = search_text.lower().strip()
            result = [n for n in result 
                     if search_lower in n.title.lower() or 
                        search_lower in n.content.lower()]
        
        return result


class NoteApp:
    """Главное приложение с GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Note Keeper - Менеджер заметок")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Инициализация хранилища
        self.storage = NoteStorage()
        
        # Категории
        self.categories = ["Все", "Работа", "Личное", "Учеба", "Идеи", "Другое"]
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление списка заметок
        self.refresh_notes_list()
    
    def setup_styles(self):
        """Настройка стилей интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'button': '#4CAF50',
            'button_hover': '#45a049',
            'error': '#f44336',
            'success': '#2196F3'
        }
        
        self.root.configure(bg=self.colors['bg'])
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Левая панель - форма добавления
        self.create_input_panel(main_frame)
        
        # Правая панель - список заметок
        self.create_notes_panel(main_frame)
        
        # Нижняя панель - фильтры
        self.create_filter_panel(main_frame)
    
    def create_input_panel(self, parent):
        """Панель для добавления заметок"""
        input_frame = ttk.LabelFrame(parent, text="Добавить заметку", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Заголовок
        ttk.Label(input_frame, text="Заголовок:*").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Категория
        ttk.Label(input_frame, text="Категория:*").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.category_combo = ttk.Combobox(input_frame, values=self.categories[1:], width=37)
        self.category_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.category_combo.set("Личное")
        
        # Приоритет
        ttk.Label(input_frame, text="Приоритет:*").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar(value="Средний")
        priority_frame = ttk.Frame(input_frame)
        priority_frame.grid(row=5, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Radiobutton(priority_frame, text="Высокий", variable=self.priority_var, 
                       value="Высокий").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Средний", variable=self.priority_var, 
                       value="Средний").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Низкий", variable=self.priority_var, 
                       value="Низкий").pack(side=tk.LEFT)
        
        # Содержание
        ttk.Label(input_frame, text="Содержание:*").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.content_text = scrolledtext.ScrolledText(input_frame, width=40, height=10, wrap=tk.WORD)
        self.content_text.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="➕ Добавить заметку", 
                                 bg=self.colors['button'], fg='white', font=('Arial', 10, 'bold'),
                                 command=self.add_note, cursor='hand2')
        self.add_btn.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Примечание об обязательных полях
        ttk.Label(input_frame, text="* - обязательные поля", font=('Arial', 8, 'italic')).grid(row=9, column=0, sticky=tk.W)
    
    def create_notes_panel(self, parent):
        """Панель со списком заметок"""
        notes_frame = ttk.LabelFrame(parent, text="Список заметок", padding="10")
        notes_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создание Treeview с прокруткой
        tree_frame = ttk.Frame(notes_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Заголовок', 'Категория', 'Приоритет', 'Дата'),
                                 show='headings', yscrollcommand=scrollbar.set, height=20)
        
        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Заголовок', text='Заголовок')
        self.tree.heading('Категория', text='Категория')
        self.tree.heading('Приоритет', text='Приоритет')
        self.tree.heading('Дата', text='Дата создания')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Заголовок', width=250)
        self.tree.column('Категория', width=120)
        self.tree.column('Приоритет', width=100, anchor='center')
        self.tree.column('Дата', width=150, anchor='center')
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Привязка двойного клика для просмотра/удаления
        self.tree.bind('<Double-Button-1>', self.view_or_delete_note)
        
        # Кнопки управления
        btn_frame = ttk.Frame(notes_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.delete_btn = tk.Button(btn_frame, text="🗑 Удалить выбранную", 
                                   bg=self.colors['error'], fg='white',
                                   command=self.delete_selected_note, cursor='hand2')
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", 
                                    bg=self.colors['success'], fg='white',
                                    command=self.refresh_notes_list, cursor='hand2')
        self.refresh_btn.pack(side=tk.LEFT)
        
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def create_filter_panel(self, parent):
        """Панель фильтрации"""
        filter_frame = ttk.LabelFrame(parent, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=(0, 10))
        self.filter_category = ttk.Combobox(filter_frame, values=self.categories, width=15)
        self.filter_category.grid(row=0, column=1, padx=(0, 20))
        self.filter_category.set("Все")
        
        # Фильтр по приоритету
        ttk.Label(filter_frame, text="Приоритет:").grid(row=0, column=2, padx=(0, 10))
        self.filter_priority = ttk.Combobox(filter_frame, values=["Все", "Высокий", "Средний", "Низкий"], width=12)
        self.filter_priority.grid(row=0, column=3, padx=(0, 20))
        self.filter_priority.set("Все")
        
        # Поиск
        ttk.Label(filter_frame, text="Поиск:").grid(row=0, column=4, padx=(0, 10))
        self.search_entry = ttk.Entry(filter_frame, width=30)
        self.search_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Кнопка фильтрации
        self.filter_btn = tk.Button(filter_frame, text="🔍 Применить фильтр", 
                                   bg=self.colors['success'], fg='white',
                                   command=self.apply_filter, cursor='hand2')
        self.filter_btn.grid(row=0, column=6)
        
        # Кнопка сброса фильтра
        self.reset_btn = tk.Button(filter_frame, text="✖ Сбросить", 
                                  command=self.reset_filter, cursor='hand2')
        self.reset_btn.grid(row=0, column=7, padx=(10, 0))
        
        # Привязка Enter для поиска
        self.search_entry.bind('<Return>', lambda e: self.apply_filter())
    
    def validate_inputs(self) -> tuple[bool, str]:
        """Валидация полей ввода"""
        title = self.title_entry.get().strip()
        if not title:
            return False, "Заголовок не может быть пустым"
        if len(title) > 100:
            return False, "Заголовок не может превышать 100 символов"
        
        content = self.content_text.get("1.0", tk.END).strip()
        if not content:
            return False, "Содержание не может быть пустым"
        if len(content) > 5000:
            return False, "Содержание не может превышать 5000 символов"
        
        category = self.category_combo.get()
        if not category:
            return False, "Выберите категорию"
        
        return True, ""
    
    def add_note(self):
        """Добавление новой заметки"""
        # Валидация
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Ошибка валидации", error_msg)
            return
        
        try:
            note = Note(
                title=self.title_entry.get().strip(),
                content=self.content_text.get("1.0", tk.END).strip(),
                priority=self.priority_var.get(),
                category=self.category_combo.get(),
                created_at="",  # Будет установлено в storage
                note_id=0  # Будет установлено в storage
            )
            
            self.storage.add_note(note)
            messagebox.showinfo("Успех", "Заметка успешно добавлена!")
            
            # Очистка полей
            self.title_entry.delete(0, tk.END)
            self.content_text.delete("1.0", tk.END)
            self.category_combo.set("Личное")
            self.priority_var.set("Средний")
            
            # Обновление списка
            self.refresh_notes_list()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить заметку: {e}")
    
    def delete_selected_note(self):
        """Удаление выбранной заметки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заметку для удаления")
            return
        
        note_id = int(self.tree.item(selected[0])['values'][0])
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту заметку?"):
            if self.storage.remove_note(note_id):
                messagebox.showinfo("Успех", "Заметка удалена")
                self.refresh_notes_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить заметку")
    
    def view_or_delete_note(self, event):
        """Просмотр или удаление по двойному клику"""
        selected = self.tree.selection()
        if not selected:
            return
        
        note_id = int(self.tree.item(selected[0])['values'][0])
        note = next((n for n in self.storage.get_all_notes() if n.note_id == note_id), None)
        
        if note:
            self.show_note_details(note)
    
    def show_note_details(self, note: Note):
        """Показать подробности заметки в отдельном окне"""
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"Заметка #{note.note_id}")
        detail_win.geometry("500x400")
        
        # Создание виджетов
        frame = ttk.Frame(detail_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(frame, text=f"Заголовок:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text=note.title, wraplength=450).pack(anchor=tk.W, pady=(0, 10))
        
        # Категория и приоритет
        info_frame = ttk.Frame(frame)
        info_frame.pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(info_frame, text=f"Категория: {note.category}").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(info_frame, text=f"Приоритет: {note.priority}").pack(side=tk.LEFT)
        
        # Дата
        ttk.Label(frame, text=f"Создано: {note.created_at}", font=('Arial', 9, 'italic')).pack(anchor=tk.W, pady=(0, 10))
        
        # Содержание
        ttk.Label(frame, text="Содержание:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert("1.0", note.content)
        content_text.config(state=tk.DISABLED)
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(btn_frame, text="Удалить", bg=self.colors['error'], fg='white',
                 command=lambda: self.delete_from_detail(detail_win, note.note_id)).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Button(btn_frame, text="Закрыть", command=detail_win.destroy).pack(side=tk.RIGHT)
    
    def delete_from_detail(self, window, note_id: int):
        """Удаление из окна деталей"""
        if messagebox.askyesno("Подтверждение", "Удалить эту заметку?"):
            if self.storage.remove_note(note_id):
                messagebox.showinfo("Успех", "Заметка удалена")
                window.destroy()
                self.refresh_notes_list()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить заметку")
    
    def refresh_notes_list(self):
        """Обновление списка заметок"""
        self.apply_filter()
    
    def apply_filter(self):
        """Применение фильтрации"""
        category = self.filter_category.get()
        priority = self.filter_priority.get()
        search_text = self.search_entry.get()
        
        filtered_notes = self.storage.filter_notes(category, priority, search_text)
        
        # Очистка Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление отфильтрованных заметок
        for note in filtered_notes:
            # Цветовая индикация приоритета
            tag = ''
            if note.priority == 'Высокий':
                tag = 'high'
            elif note.priority == 'Низкий':
                tag = 'low'
            
            self.tree.insert('', tk.END, values=(note.note_id, note.title[:50], 
                                                note.category, note.priority, note.created_at),
                           tags=(tag,))
        
        # Настройка тегов
        self.tree.tag_configure('high', background='#ffcccc')
        self.tree.tag_configure('low', background='#ccffcc')
        
        # Обновление статуса
        count = len(filtered_notes)
        total = len(self.storage.get_all_notes())
        self.root.title(f"Note Keeper - {count} из {total} заметок")
    
    def reset_filter(self):
        """Сброс всех фильтров"""
        self.filter_category.set("Все")
        self.filter_priority.set("Все")
        self.search_entry.delete(0, tk.END)
        self.apply_filter()


# Модульные тесты
class TestNoteSystem(unittest.TestCase):
    """Тестирование функциональности заметок"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_file = "test_notes.json"
        self.storage = NoteStorage(self.test_file)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_create_valid_note(self):
        """Позитивный тест: создание валидной заметки"""
        note = Note(
            title="Тестовая заметка",
            content="Это тестовое содержание",
            priority="Средний",
            category="Тест",
            created_at="",
            note_id=0
        )
        self.assertEqual(note.title, "Тестовая заметка")
    
    def test_invalid_title_empty(self):
        """Негативный тест: пустой заголовок"""
        with self.assertRaises(ValueError):
            Note(title="", content="Контент", priority="Средний", 
                category="Тест", created_at="", note_id=0)
    
    def test_invalid_title_too_long(self):
        """Негативный тест: слишком длинный заголовок"""
        long_title = "A" * 101
        with self.assertRaises(ValueError):
            Note(title=long_title, content="Контент", priority="Средний",
                category="Тест", created_at="", note_id=0)
    
    def test_invalid_priority(self):
        """Граничный тест: некорректный приоритет"""
        with self.assertRaises(ValueError):
            Note(title="Тест", content="Контент", priority="Неверный",
                category="Тест", created_at="", note_id=0)
    
    def test_add_note_to_storage(self):
        """Позитивный тест: добавление заметки в хранилище"""
        note = Note(title="Тест", content="Контент", priority="Средний",
                   category="Тест", created_at="", note_id=0)
        success = self.storage.add_note(note)
        self.assertTrue(success)
        self.assertEqual(len(self.storage.get_all_notes()), 1)
    
    def test_remove_note(self):
        """Позитивный тест: удаление заметки"""
        note = Note(title="Тест", content="Контент", priority="Средний",
                   category="Тест", created_at="", note_id=0)
        self.storage.add_note(note)
        note_id = self.storage.get_all_notes()[0].note_id
        success = self.storage.remove_note(note_id)
        self.assertTrue(success)
        self.assertEqual(len(self.storage.get_all_notes()), 0)
    
    def test_filter_by_category(self):
        """Позитивный тест: фильтрация по категории"""
        note1 = Note(title="Работа", content="Контент1", priority="Высокий",
                    category="Работа", created_at="", note_id=0)
        note2 = Note(title="Личное", content="Контент2", priority="Низкий",
                    category="Личное", created_at="", note_id=0)
        self.storage.add_note(note1)
        self.storage.add_note(note2)
        
        filtered = self.storage.filter_notes(category="Работа")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].category, "Работа")
    
    def test_search_filter(self):
        """Граничный тест: поиск по тексту"""
        note = Note(title="Важная заметка", content="Содержание с ключевым словом",
                   priority="Высокий", category="Работа", created_at="", note_id=0)
        self.storage.add_note(note)
        
        filtered = self.storage.filter_notes(search_text="ключевым")
        self.assertEqual(len(filtered), 1)
    
    def test_empty_search(self):
        """Граничный тест: пустой поиск"""
        note = Note(title="Тест", content="Контент", priority="Средний",
                   category="Тест", created_at="", note_id=0)
        self.storage.add_note(note)
        
        filtered = self.storage.filter_notes(search_text="")
        self.assertEqual(len(filtered), 1)


def run_tests():
    """Запуск тестов"""
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNoteSystem)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Главная функция приложения"""
    # Спрашиваем, запускать ли тесты
    print("Note Keeper - Менеджер заметок")
    print("Автор: Иван Иванов")
    print("Версия: 1.0.0")
    print("-" * 50)
    
    run_tests_choice = input("Запустить тесты перед стартом? (y/n): ").lower()
    if run_tests_choice == 'y':
        print("\nЗапуск тестов...")
        if run_tests():
            print("✅ Все тесты пройдены успешно!\n")
        else:
            print("❌ Некоторые тесты не пройдены. Продолжить? (y/n): ")
            if input().lower() != 'y':
                return
    
    # Запуск GUI
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
Инструкция по запуску и README для GitHub
Создайте файл README.md для вашего репозитория:

markdown
# Note Keeper - Менеджер заметок

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Описание проекта

**Note Keeper** - это десктопное приложение для управления заметками с графическим интерфейсом, разработанное на Python с использованием Tkinter. Приложение позволяет создавать, хранить, фильтровать и удалять заметки с автоматическим сохранением в JSON-файл.

### Возможности

- ✅ Создание заметок с заголовком, содержанием, категорией и приоритетом
- ✅ Автоматическая валидация ввода данных
- ✅ Фильтрация заметок по категории, приоритету и поиску по тексту
- ✅ Цветовая индикация приоритета (высокий - красный, низкий - зеленый)
- ✅ Просмотр полного содержания заметки в отдельном окне
- ✅ Сохранение и загрузка данных в JSON формате
- ✅ Модульное тестирование всех функций
- ✅ Интуитивно понятный интерфейс

### Технологии

- Python 3.7+
- Tkinter (GUI)
- JSON (хранение данных)
- unittest (тестирование)
- dataclasses

## Установка и запуск

### Требования

- Python 3.7 или выше
- Tkinter (обычно входит в стандартную установку Python)

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/note-keeper.git
cd note-keeper
