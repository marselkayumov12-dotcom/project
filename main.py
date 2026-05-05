import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Data storage
        self.quotes = []
        self.history = []
        self.filtered_quotes = []
        
        # Load data
        self.load_initial_quotes()
        self.load_history()
        
        # Setup UI
        self.setup_ui()
        
    def load_initial_quotes(self):
        """Load predefined quotes"""
        self.quotes = [
            {"text": "Be the change that you wish to see in the world.", "author": "Mahatma Gandhi", "topic": "Inspiration"},
            {"text": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt", "topic": "Motivation"},
            {"text": "In the end, it's not the years in your life that count. It's the life in your years.", "author": "Abraham Lincoln", "topic": "Life"},
            {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt", "topic": "Dreams"},
            {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill", "topic": "Success"},
            {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "topic": "Career"},
            {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "topic": "Life"},
            {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu", "topic": "Inspiration"},
            {"text": "Keep calm and carry on.", "author": "British Government", "topic": "Motivation"},
            {"text": "Imagination is more important than knowledge.", "author": "Albert Einstein", "topic": "Wisdom"},
        ]
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Quote display area
        quote_frame = ttk.LabelFrame(main_frame, text="Current Quote", padding="10")
        quote_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.quote_text = tk.Text(quote_frame, height=4, wrap=tk.WORD, font=("Arial", 12))
        self.quote_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.author_label = ttk.Label(quote_frame, text="Author: ", font=("Arial", 10, "italic"))
        self.author_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.topic_label = ttk.Label(quote_frame, text="Topic: ", font=("Arial", 10))
        self.topic_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.generate_btn = ttk.Button(button_frame, text="Generate Random Quote", command=self.generate_quote)
        self.generate_btn.grid(row=0, column=0, padx=5)
        
        self.add_btn = ttk.Button(button_frame, text="Add New Quote", command=self.add_quote_dialog)
        self.add_btn.grid(row=0, column=1, padx=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(filter_frame, text="Filter by Author:").grid(row=0, column=0, padx=5)
        self.author_filter = ttk.Combobox(filter_frame, values=self.get_unique_authors(), width=20)
        self.author_filter.grid(row=0, column=1, padx=5)
        self.author_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        ttk.Label(filter_frame, text="Filter by Topic:").grid(row=0, column=2, padx=5)
        self.topic_filter = ttk.Combobox(filter_frame, values=self.get_unique_topics(), width=20)
        self.topic_filter.grid(row=0, column=3, padx=5)
        self.topic_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).grid(row=0, column=4, padx=5)
        
        # History display
        history_frame = ttk.LabelFrame(main_frame, text="Quote History", padding="10")
        history_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, height=12)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Update displays
        self.update_history_display()
        self.generate_quote()
        
    def get_unique_authors(self):
        """Get unique authors from quotes"""
        return sorted(set(quote["author"] for quote in self.quotes))
    
    def get_unique_topics(self):
        """Get unique topics from quotes"""
        return sorted(set(quote["topic"] for quote in self.quotes))
    
    def generate_quote(self):
        """Generate a random quote"""
        if self.filtered_quotes:
            quote = random.choice(self.filtered_quotes)
        elif self.quotes:
            quote = random.choice(self.quotes)
        else:
            self.quote_text.delete(1.0, tk.END)
            self.quote_text.insert(1.0, "No quotes available!")
            self.author_label.config(text="Author: -")
            self.topic_label.config(text="Topic: -")
            return
        
        # Display quote
        self.quote_text.delete(1.0, tk.END)
        self.quote_text.insert(1.0, quote["text"])
        self.author_label.config(text=f"Author: {quote['author']}")
        self.topic_label.config(text=f"Topic: {quote['topic']}")
        
        # Add to history
        history_entry = {
            "text": quote["text"],
            "author": quote["author"],
            "topic": quote["topic"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()
        
    def update_history_display(self):
        """Update the history listbox"""
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.history[-20:]):  # Show last 20 quotes
            display_text = f"[{entry['timestamp']}] {entry['author']}: {entry['text'][:50]}..."
            self.history_listbox.insert(tk.END, display_text)
    
    def apply_filters(self, event=None):
        """Apply author and topic filters"""
        selected_author = self.author_filter.get()
        selected_topic = self.topic_filter.get()
        
        self.filtered_quotes = self.quotes.copy()
        
        if selected_author and selected_author != "":
            self.filtered_quotes = [q for q in self.filtered_quotes if q["author"] == selected_author]
        
        if selected_topic and selected_topic != "":
            self.filtered_quotes = [q for q in self.filtered_quotes if q["topic"] == selected_topic]
        
        if not self.filtered_quotes:
            messagebox.showwarning("No Results", "No quotes match the selected filters!")
        
        self.generate_quote()
    
    def clear_filters(self):
        """Clear all filters"""
        self.author_filter.set('')
        self.topic_filter.set('')
        self.filtered_quotes = []
        self.generate_quote()
        
        # Update filter dropdowns
        self.author_filter['values'] = self.get_unique_authors()
        self.topic_filter['values'] = self.get_unique_topics()
    
    def add_quote_dialog(self):
        """Open dialog to add new quote"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Quote")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Quote text
        ttk.Label(dialog, text="Quote Text:").pack(pady=5)
        text_entry = tk.Text(dialog, height=5, width=60)
        text_entry.pack(pady=5)
        
        # Author
        ttk.Label(dialog, text="Author:").pack(pady=5)
        author_entry = ttk.Entry(dialog, width=40)
        author_entry.pack(pady=5)
        
        # Topic
        ttk.Label(dialog, text="Topic:").pack(pady=5)
        topics = ["Inspiration", "Motivation", "Life", "Dreams", "Success", "Career", "Wisdom", "Love", "Friendship"]
        topic_combo = ttk.Combobox(dialog, values=topics, width=37)
        topic_combo.pack(pady=5)
        
        def save_quote():
            text = text_entry.get(1.0, tk.END).strip()
            author = author_entry.get().strip()
            topic = topic_combo.get().strip()
            
            # Validation
            if not text:
                messagebox.showerror("Error", "Quote text cannot be empty!")
                return
            if not author:
                messagebox.showerror("Error", "Author cannot be empty!")
                return
            if not topic:
                messagebox.showerror("Error", "Topic cannot be empty!")
                return
            
            # Add new quote
            new_quote = {"text": text, "author": author, "topic": topic}
            self.quotes.append(new_quote)
            
            # Save to JSON
            self.save_quotes()
            
            # Update filters
            self.author_filter['values'] = self.get_unique_authors()
            self.topic_filter['values'] = self.get_unique_topics()
            
            dialog.destroy()
            messagebox.showinfo("Success", "Quote added successfully!")
        
        ttk.Button(dialog, text="Save Quote", command=save_quote).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
    
    def save_quotes(self):
        """Save quotes to JSON file"""
        try:
            with open('quotes.json', 'w', encoding='utf-8') as f:
                json.dump(self.quotes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving quotes: {e}")
    
    def save_history(self):
        """Save history to JSON file"""
        try:
            with open('history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from JSON file"""
        try:
            if os.path.exists('history.json'):
                with open('history.json', 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
