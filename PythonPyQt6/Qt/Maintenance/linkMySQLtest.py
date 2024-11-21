import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """
    建立與 MySQL 資料庫的連線，並回傳連線物件。
    """
    try:
        # 填寫資料庫連線資訊
        connection = mysql.connector.connect(
            host="192.168.1.138",  # 資料庫主機地址 (例如: "192.168.1.138")
            user="Administrator",       # 資料庫使用者名稱
            password="Yoyo1597531@",  # 資料庫密碼
            database="Maintenance"  # 要連線的資料庫名稱
        )
        if connection.is_connected():
            print("成功連接到資料庫")
        return connection
    except Error as e:
        print(f"連線失敗，錯誤訊息: {e}")
        return None

def fetch_data(connection):
    """
    從資料庫中讀取資料並列印到控制台。
    """
    try:
        # 建立游標
        cursor = connection.cursor()
        # 填寫要執行的 SQL 查詢
        query = "SELECT * FROM Status;"  # 替換為你的表格名稱
        cursor.execute(query)

        # 獲取查詢結果
        rows = cursor.fetchall()
        print(f"查詢到 {len(rows)} 筆資料:")

        # 列印每筆資料
        for row in rows:
            print(row)

    except Error as e:
        print(f"查詢失敗，錯誤訊息: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    """
    主函式：建立連線、讀取資料並關閉連線。
    """
    connection = connect_to_database()
    if connection:
        fetch_data(connection)
        # 關閉資料庫連線
        connection.close()
        print("資料庫連線已關閉")

if __name__ == "__main__":
    main()
