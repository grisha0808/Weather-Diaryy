import json
import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "conversion_history.json"

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter - Конвертер валют")
        self.root.geometry("750x550")
        self.root.resizable(False, False)
        
        self.history = []
        self.load_history()
        
        # Доступные валюты
        self.currencies = ["USD", "EUR", "RUB", "KZT", "GBP", "CNY", "JPY", "TRY", "UAH", "BYN"]
        
        # API ключ (замените на свой)
        self.api_key = "YOUR_API_KEY_HERE"
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.root, text="Конвертер валют", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Рамка для конвертации
        convert_frame = tk.LabelFrame(self.root, text="Конвертация", padx=15, pady=15, font=("Arial", 10, "bold"))
        convert_frame.pack(fill="x", padx=20, pady=10)
        
        # Сумма
        tk.Label(convert_frame, text="Сумма:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.amount_entry = tk.Entry(convert_frame, width=15, font=("Arial", 11))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Из какой валюты
        tk.Label(convert_frame, text="Из валюты:", font=("Arial", 11)).grid(row=0, column=2, sticky="w", padx=(15,0), pady=5)
        self.from_currency = ttk.Combobox(convert_frame, values=self.currencies, width=8, font=("Arial", 11))
        self.from_currency.set("USD")
        self.from_currency.grid(row=0, column=3, padx=5, pady=5)
        
        # Стрелка
        tk.Label(convert_frame, text="→", font=("Arial", 14)).grid(row=0, column=4, padx=5)
        
        # В какую валюту
        tk.Label(convert_frame, text="В валюту:", font=("Arial", 11)).grid(row=0, column=5, sticky="w", pady=5)
        self.to_currency = ttk.Combobox(convert_frame, values=self.currencies, width=8, font=("Arial", 11))
        self.to_currency.set("EUR")
        self.to_currency.grid(row=0, column=6, padx=5, pady=5)
        
        # Кнопка конвертации
        self.convert_btn = tk.Button(convert_frame, text="Конвертировать", command=self.convert, 
                                      bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=15)
        self.convert_btn.grid(row=0, column=7, padx=15, pady=5)
        
        # Рамка для результата
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(result_frame, text="Результат:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.result_label = tk.Label(result_frame, text="0.00", font=("Arial", 14, "bold"), fg="#2196F3")
        self.result_label.pack(side="left", padx=5)
        
        # Рамка для истории
        history_frame = tk.LabelFrame(self.root, text="История конвертаций", padx=10, pady=10, font=("Arial", 10, "bold"))
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Таблица истории
        columns = ("date", "amount", "from_cur", "to_cur", "rate", "result")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("from_cur", text="Из")
        self.tree.heading("to_cur", text="В")
        self.tree.heading("rate", text="Курс")
        self.tree.heading("result", text="Результат")
        
        self.tree.column("date", width=140)
        self.tree.column("amount", width=80)
        self.tree.column("from_cur", width=60)
        self.tree.column("to_cur", width=60)
        self.tree.column("rate", width=100)
        self.tree.column("result", width=100)
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка очистки истории
        clear_btn = tk.Button(self.root, text="Очистить историю", command=self.clear_history,
                               bg="#f44336", fg="white", font=("Arial", 10))
        clear_btn.pack(pady=5)
        
        self.refresh_history()
    
    def validate_amount(self):
        """Проверка корректности ввода суммы"""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return None
            return amount
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число")
            return None
    
    def get_exchange_rate(self, from_cur, to_cur):
        """Получение курса валют из API"""
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_cur}/{to_cur}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "success":
                    return data.get("conversion_rate")
                else:
                    messagebox.showerror("Ошибка", "API вернул ошибку. Проверьте API ключ.")
                    return None
            else:
                messagebox.showerror("Ошибка API", f"Код ошибки: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API.\n{str(e)}")
            return None
    
    def convert(self):
        """Основная функция конвертации"""
        # Проверка суммы
        amount = self.validate_amount()
        if amount is None:
            return
        
        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        
        # Если валюты одинаковые
        if from_cur == to_cur:
            result = amount
            rate = 1
        else:
            rate = self.get_exchange_rate(from_cur, to_cur)
            if rate is None:
                return
            result = amount * rate
        
        # Отображение результата
        self.result_label.config(text=f"{result:.2f} {to_cur}")
        
        # Сохранение в историю
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_cur": from_cur,
            "to_cur": to_cur,
            "rate": round(rate, 4),
            "result": round(result, 2)
        }
        self.history.append(record)
        self.save_history()
        self.refresh_history()
        
        # Очистка поля ввода
        self.amount_entry.delete(0, tk.END)
    
    def refresh_history(self):
        """Обновление таблицы истории"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for rec in reversed(self.history):  # Новые записи сверху
            self.tree.insert("", tk.END, values=(
                rec["date"],
                f"{rec['amount']:.2f}",
                rec["from_cur"],
                rec["to_cur"],
                f"{rec['rate']:.4f}",
                f"{rec['result']:.2f}"
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history()
            messagebox.showinfo("Успех", "История очищена")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []
    
    def save_history(self):
        """Сохранение истории в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
    
    def on_closing(self):
        """Действие при закрытии окна"""
        self.save_history()
        self.root.destroy()

# Точка входа
if name == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
