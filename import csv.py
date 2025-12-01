import csv
import os
from datetime import datetime

# 定義資料儲存的檔案名稱
DATA_FILE = 'expenses.csv'

def add_expense():
    print("=== 新增支出紀錄 ===")
    
    # 1. 輸入日期 (預設為今天，或手動輸入)
    date_str = input("請輸入日期 (YYYY-MM-DD，直接按 Enter 使用今日): ")
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2. 輸入金額
    while True:
        try:
            amount = float(input("請輸入金額: "))
            break
        except ValueError:
            print("金額格式錯誤，請輸入數字。")

    # 3. 輸入類別
    category = input("請輸入類別 (例如: 食物, 交通, 娛樂): ")
    
    # 4. 輸入備註 (選填) [cite: 8]
    notes = input("請輸入備註 (選填): ")

    # 檢查檔案是否存在，若不存在則寫入標題
    file_exists = os.path.isfile(DATA_FILE)
    
    # 寫入 CSV 檔案
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 寫入標題列 (如果是新檔案)
            if not file_exists:
                writer.writerow(["Date", "Amount", "Category", "Notes"])
            
            # 寫入資料
            writer.writerow([date_str, amount, category, notes])
            print(f"成功儲存: {date_str} - {category} - ${amount}")
    except Exception as e:
        print(f"寫入檔案時發生錯誤: {e}")

def main():
    while True:
        add_expense()
        cont = input("\n要繼續新增下一筆嗎？ (y/n): ")
        if cont.lower() != 'y':
            break
    print("輸入結束。")

if __name__ == "__main__":
    main()