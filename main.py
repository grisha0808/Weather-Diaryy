import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("750x500")

        self.records = []
        self.load_data()

        self.create_input_frame()
        self.create_filter_frame()
        self.create_records_tree()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except:
                self.records = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    def validate_input(self, date_str, temp_str, description, precipitation):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return False
        try:
            float(temp_str)
        except:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return False
        if not description.strip():
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return False
        return True

    def add_record(self):
        date = self.entry_date.get()
        temp = self.entry_temp.get()
        description = self.entry_desc.get()
        precipitation = "Да" if self.precip_var.get() else "Нет"

        if not self.validate_input(date, temp, description, precipitation):
            return

        record = {
            "date": date,
            "temperature": float(temp),
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        self.save_data()
        self.refresh_tree()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.entry_date.delete(0, tk.END)
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.precip_var.set(False)

    def filter_records(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            filtered = [r for r in filtered if r["date"] == filter_date]

        if filter_temp:
            try:
                temp_val = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_val]
            except:
                messagebox.showerror("Ошибка", "Температура для фильтра должна быть числом")
                return

        self.refresh_tree(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_tree(self.records)

    def refresh_tree(self, records_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if records_to_show is None:
            records_to_show = self.records

        for rec in records_to_show:
            self.tree.insert("", tk.END, values=(
                rec["date"],
                f"{rec['temperature']:.1f}°C",
                rec["description"],
                rec["precipitation"]
            ))

    def create_input_frame(self):
        frame = tk.LabelFrame(self.root, text="Добавление записи", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.entry_date = tk.Entry(frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.entry_temp = tk.Entry(frame, width=8)
        self.entry_temp.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Описание:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.entry_desc = tk.Entry(frame, width=40)
        self.entry_desc.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=(5,0))

        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Осадки (да/нет)", variable=self.precip_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(5,0))

        tk.Button(frame, text="Добавить запись", command=self.add_record, bg="lightgreen").grid(row=2, column=2, pady=(5,0), padx=10)

    def create_filter_frame(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по дате (точное совпадение):").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = tk.Entry(frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Фильтр по температуре (выше, °C):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.filter_temp_entry = tk.Entry(frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        tk.Button(frame, text="Применить фильтр", command=self.filter_records).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5)

    def create_records_tree(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_tree()

    def on_closing(self):
        self.save_data()
        self.root.destroy()

if name == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
