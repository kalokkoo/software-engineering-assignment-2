import csv
import matplotlib.pyplot as plt
import os
from collections import defaultdict

# 定義資料來源檔案
DATA_FILE = 'expenses.csv'

def generate_pie_chart():
    # 檢查資料檔是否存在
    if not os.path.exists(DATA_FILE):
        print(f"找不到資料檔 {DATA_FILE}。請先執行輸入模組新增資料。")
        return

    category_totals = defaultdict(float)

    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            row_count = 0
            for row in reader:
                try:
                    category = row['Category']
                    amount = float(row['Amount'])
                    category_totals[category] += amount
                    row_count += 1
                except ValueError:
                    continue # 跳過資料毀損的行
            
            if row_count == 0:
                print("檔案中沒有資料可供繪圖。")
                return

    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        return

    # 準備繪圖資料
    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    # 設定中文字型 (選用，避免中文亂碼，視作業系統而定)
    # plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    # plt.rcParams['axes.unicode_minus'] = False

    # 繪製圓餅圖 
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # 確保圓餅圖是圓形
    plt.title('Expense Distribution by Category')
    
    print("正在生成圓餅圖...")
    plt.show()

if __name__ == "__main__":
    generate_pie_chart()