import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import platform
from datetime import datetime

# --- 定義資料儲存的檔案名稱 (與 input.py 相同) ---
DATA_FILE = 'expenses.csv'

# --- 設定中文字型 (嘗試跨平台相容) ---
def get_chinese_font():
    system = platform.system()
    if system == "Windows":
        return 'Microsoft JhengHei' # 微軟正黑體
    elif system == "Darwin": # macOS
        return 'Arial Unicode MS'
    elif system == "Linux":
        return 'WenQuanYi Micro Hei'
    return 'sans-serif'

# 設定 Matplotlib 字型
CHINESE_FONT = get_chinese_font()
plt.rcParams['font.sans-serif'] = [CHINESE_FONT]
plt.rcParams['axes.unicode_minus'] = False

# --- 輔助函式：金額正規化 ---
def normalize_amount(amount_str):
    if not amount_str:
        return ""
    table = str.maketrans('０１２３４５６７８９', '0123456789')
    amount_str = amount_str.translate(table)
    amount_str = amount_str.replace(',', '').strip()
    return amount_str

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("記帳管理系統")
        self.root.geometry("1100x700") 

        # 確保資料檔存在，標頭需與 input.py 一致: Date, Amount, Category, Notes
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Amount", "Category", "Notes"])

        # --- 版面配置 ---
        self.left_frame = ttk.Frame(root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 輸入區 ---
        input_frame = ttk.LabelFrame(self.left_frame, text="編輯支出", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 1. 日期 (新增)
        ttk.Label(input_frame, text="日期:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        # 預設填入今天日期
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

        # 2. 類別
        ttk.Label(input_frame, text="類別:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.category_var = tk.StringVar()
        self.category_entry = ttk.Entry(input_frame, textvariable=self.category_var)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # 3. 金額
        ttk.Label(input_frame, text="金額:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # 4. 備註 (對應 input.py 的 Notes)
        ttk.Label(input_frame, text="備註:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(input_frame, textvariable=self.notes_var, width=30)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # 按鈕區
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="新增", command=self.add_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="修改選取", command=self.update_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刪除選取", command=self.delete_expense).pack(side=tk.LEFT, padx=5)

        # --- 列表區 ---
        list_frame = ttk.LabelFrame(self.left_frame, text="支出明細", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 定義欄位：對應 Date, Amount, Category, Notes
        columns = ('date', 'category', 'amount', 'notes')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading('date', text='日期')
        self.tree.heading('category', text='類別')
        self.tree.heading('amount', text='金額')
        self.tree.heading('notes', text='備註') 
        
        self.tree.column('date', width=90, anchor='center')
        self.tree.column('category', width=80, anchor='center')
        self.tree.column('amount', width=80, anchor='e')
        self.tree.column('notes', width=150, anchor='w')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 圖表區 ---
        self.figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.load_data()

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            vals = item['values']
            # vals 順序: date, category, amount, notes
            self.date_var.set(vals[0])
            self.category_var.set(vals[1])
            self.amount_var.set(vals[2])
            # 處理可能沒有備註的情況
            if len(vals) > 3:
                self.notes_var.set(vals[3])
            else:
                self.notes_var.set("")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.data = []
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 相容性處理：嘗試讀取不同欄位名稱
                for row in reader:
                    # 優先使用 input.py 的命名 (Notes)，若無則找舊版 (Remark)
                    date_val = row.get('Date', '')
                    cat = row.get('Category', '')
                    amt = row.get('Amount', '0')
                    note = row.get('Notes', row.get('Remark', ''))
                    
                    self.data.append({'Date': date_val, 'Category': cat, 'Amount': amt, 'Notes': note})
                    self.tree.insert('', tk.END, values=(date_val, cat, amt, note))
        except Exception as e:
            print(f"讀取提示: {e}")

        self.draw_chart()

    def save_data(self):
        # 寫入時使用標準欄位: Date, Amount, Category, Notes
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Date', 'Amount', 'Category', 'Notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.data:
                # 確保寫入時字典key與fieldnames一致
                writer.writerow({
                    'Date': row.get('Date', ''),
                    'Amount': row.get('Amount', 0),
                    'Category': row.get('Category', ''),
                    'Notes': row.get('Notes', '')
                })
        
        self.load_data()

    def add_expense(self):
        date_val = self.date_var.get().strip()
        cat = self.category_var.get().strip()
        raw_amt = self.amount_var.get()
        note = self.notes_var.get().strip()
        
        amt_str = normalize_amount(raw_amt)

        if not date_val:
            date_val = datetime.now().strftime("%Y-%m-%d") # 若為空則補今天
        
        if not cat:
            messagebox.showwarning("錯誤", "請輸入類別")
            return
        
        if not amt_str:
             messagebox.showwarning("錯誤", "請輸入金額")
             return

        try:
            float(amt_str)
            self.data.append({'Date': date_val, 'Category': cat, 'Amount': amt_str, 'Notes': note})
            self.save_data()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("錯誤", f"金額格式錯誤: '{raw_amt}'")

    def update_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "請先選擇要修改的項目")
            return
        
        index = self.tree.index(selected_item)
        
        date_val = self.date_var.get().strip()
        cat = self.category_var.get().strip()
        raw_amt = self.amount_var.get()
        note = self.notes_var.get().strip()
        
        amt_str = normalize_amount(raw_amt)
        
        if not cat:
            messagebox.showwarning("錯誤", "類別不能為空")
            return

        try:
            float(amt_str)
            self.data[index] = {'Date': date_val, 'Category': cat, 'Amount': amt_str, 'Notes': note}
            self.save_data()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("錯誤", f"金額格式錯誤: '{raw_amt}'")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("提示", "請先選擇要刪除的項目")
            return
        
        if messagebox.askyesno("確認", "確定要刪除這筆資料嗎？"):
            index = self.tree.index(selected_item)
            del self.data[index]
            self.save_data()
            self.clear_inputs()

    def clear_inputs(self):
        self.category_var.set("")
        self.amount_var.set("")
        self.notes_var.set("")
        # 日期通常不需要清空，或是重設為今天
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    def draw_chart(self):
        self.ax.clear()
        
        if not self.data:
            self.ax.text(0.5, 0.5, '尚無資料', ha='center', va='center', fontproperties=CHINESE_FONT)
            self.canvas.draw()
            return

        category_totals = {}
        for row in self.data:
            cat = row['Category']
            try:
                amt = float(row['Amount'])
                category_totals[cat] = category_totals.get(cat, 0) + amt
            except:
                continue

        if not category_totals or sum(category_totals.values()) == 0:
            self.ax.text(0.5, 0.5, '無有效金額資料', ha='center', va='center', fontproperties=CHINESE_FONT)
            self.canvas.draw()
            return

        labels = list(category_totals.keys())
        sizes = list(category_totals.values())
        
        colors = plt.cm.Pastel1(range(len(labels)))
        
        wedges, texts, autotexts = self.ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90,
            colors=colors,
            pctdistance=0.85, 
            wedgeprops=dict(width=0.4, edgecolor='w'), 
            textprops={'fontsize': 10}
        )

        plt.setp(texts, size=10)
        plt.setp(autotexts, size=9, weight="bold", color="black")

        self.ax.set_title('支出類別分佈', fontsize=14, pad=20)
        self.ax.axis('equal') 
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()