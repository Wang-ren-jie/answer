import mysql.connector
from mysql.connector import Error
from PyQt6 import QtWidgets, QtCore
from maintenance import Ui_MaintenanceWindow  # 導入生成的 UI 類
import datetime

class MaintenanceApp(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.m_ui = Ui_MaintenanceWindow()
        self.m_ui.setupUi(self)

        # 初始化 MySQL 連線
        self.m_db_connection = self.connectToDatabase()
        self.cursor = self.m_db_connection.cursor()

        

        # 設定表格標題與初始化
        self.m_ui.tableWidget_log.setColumnCount(7)  # 7 列
        self.m_ui.tableWidget_log.setHorizontalHeaderLabels(
            ["編號", "日期", "廠區", "機台使用位置", "請修狀況", "申報人員", "請修狀況說明"]
        )
        self.m_ui.tableWidget_log.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.m_ui.tableWidget_log.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 初始化下拉選單
        self.populateCombobox()

        # 按鈕功能連結
        self.m_ui.button_add.clicked.connect(self.addRecord)
        self.m_ui.button_delete.clicked.connect(self.deleteRecord)
        self.m_ui.button_update.clicked.connect(self.updateRecord)
        self.m_ui.button_search.clicked.connect(self.searchRecords)
        self.m_ui.tableWidget_log.itemSelectionChanged.connect(self.loadSelectedRecord)

        # 初始化資料
        self.m_records = []
        self.m_auto_increment_id = 1  # 編號起始值
        self.m_ui.date_time.setDateTime(QtCore.QDateTime.currentDateTime())  # 預設當前時間
        self.loadRecordsFromDatabase()
        
        # 當日期變化時清空其他條件
        self.m_ui.date_time.dateChanged.connect(self.clearOtherFilters)

    def updateTableView(self, records=None) -> None:
        """更新表格顯示"""
        if records is None:
            records = self.m_records

        # 清空表格並設置行數
        self.m_ui.tableWidget_log.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, value in enumerate(record):
                # 如果值是 datetime 類型，轉換為字符串
                if isinstance(value, datetime.datetime):
                    value : str = value.strftime("%Y/%m/%d %H:%M:%S")  # 轉換為指定格式的字符串
                elif value is None:
                    value : str = ""  # 如果值為 None，轉換為空字符串

                item = QtWidgets.QTableWidgetItem(value)
                # 設置表格內容為只讀
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.m_ui.tableWidget_log.setItem(row_idx, col_idx, item)


    def updateAutoIncrementId(self, date: QtCore.QDate) -> None:
        """根據選定日期更新自動遞增尾碼"""
        # 過濾出以選定日期開頭的記錄
        date_str = date.toString("yyyyMMdd")
        query = "SELECT MAX(CAST(SUBSTRING_INDEX(id, '-', -1) AS UNSIGNED)) FROM Maintenance WHERE id LIKE %s"
        try:
            self.cursor.execute(query, (f"{date_str}-%",))
            result = self.cursor.fetchone()[0]
            if result:
                self.m_auto_increment_id = int(result) + 1
            else:
                self.m_auto_increment_id = 1
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "錯誤", f"更新編號自動遞增值失敗：{e}")

    def generateId(self, date: QtCore.QDate) -> str:
        """生成新的編號，格式為 [選定日期-編號]"""
        date_str = date.toString("yyyyMMdd")  # 選定日期格式
        self.updateAutoIncrementId(date)  # 確保更新自動遞增尾碼
        return f"{date_str}-{self.m_auto_increment_id}"

    def clearOtherFilters(self) -> None:
        """當日期選擇改變時，清空其他查詢條件"""
        self.m_ui.text_number.clear()  # 清空編號
        self.m_ui.combobox_factory.setCurrentIndex(0)  # 清空廠區選擇
        self.m_ui.text_location.clear()  # 清空機台位置
        self.m_ui.combobox_status.setCurrentIndex(0)  # 清空請修狀況選擇
        self.m_ui.combobox_personnel.setCurrentIndex(0)  # 清空申報人員選擇
        self.m_ui.text_description.clear()  # 清空請修狀況說明

    def loadSelectedRecord(self) -> None:
        """選定資料並加載至輸入框"""
        selected_rows : list = self.m_ui.tableWidget_log.selectedItems()
        if not selected_rows:
            return

        # 獲取選定行索引
        row_index : int = selected_rows[0].row()

        # 從表格中提取資料
        selected_record : list = [
            self.m_ui.tableWidget_log.item(row_index, col_idx).text()
            for col_idx in range(self.m_ui.tableWidget_log.columnCount())
        ]

        # 將資料加載到對應的輸入框
        self.m_ui.text_number.setText(selected_record[0])
        self.m_ui.date_time.setDateTime(QtCore.QDateTime.fromString(selected_record[1], "yyyy-MM-dd hh:mm:ss"))
        self.m_ui.combobox_factory.setCurrentText(selected_record[2])
        self.m_ui.text_location.setText(selected_record[3])
        self.m_ui.combobox_status.setCurrentText(selected_record[4])
        self.m_ui.combobox_personnel.setCurrentText(selected_record[5])
        self.m_ui.text_description.setText(selected_record[6])



    def connectToDatabase(self):
        """建立與 MySQL 資料庫的連線"""
        try:
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
            print(f"連接資料庫失敗：{e}")
            return None

    def populateCombobox(self) -> None:
        """從 MySQL 提取資料並填充到 ComboBox"""
        try:
            # 填充廠區
            self.cursor.execute("SELECT factory FROM Factory")
            factories : list = self.cursor.fetchall()
            self.m_ui.combobox_factory.addItem("")
            for factory in factories:
                self.m_ui.combobox_factory.addItem(factory[0])

            # 填充請修狀況
            self.cursor.execute("SELECT status FROM Status")
            statuses : list = self.cursor.fetchall()
            self.m_ui.combobox_status.addItem("")
            for status in statuses:
                self.m_ui.combobox_status.addItem(status[0])

            # 填充申報人員
            self.cursor.execute("SELECT name FROM Personnel")
            personnel : list = self.cursor.fetchall()
            self.m_ui.combobox_personnel.addItem("")
            for person in personnel:
                self.m_ui.combobox_personnel.addItem(person[0])
        except Error as e:
            print(f"資料提取失敗：{e}")

    def loadRecordsFromDatabase(self) -> None:
        """從資料庫中載入今天的記錄到表格"""
        try:
            # 取得今天的日期
            today_date : str = datetime.datetime.now().strftime("%Y/%m/%d")

            # 查詢今天日期的記錄
            query : str = "SELECT * FROM Maintenance WHERE DATE(Create_time) = %s"
            self.cursor.execute(query, (today_date,))
            self.m_records : list = self.cursor.fetchall()

            # 更新表格顯示
            self.updateTableView()
        except Error as e:
            print(f"載入資料失敗：{e}")

    def extractData(self) -> str :
        """提取表格中的資料"""
        factory : str = self.m_ui.combobox_factory.currentText()
        location : str = self.m_ui.text_location.toPlainText().strip()
        status : str = self.m_ui.combobox_status.currentText()
        personnel : str = self.m_ui.combobox_personnel.currentText()
        description : str = self.m_ui.text_description.toPlainText().strip()
        return factory, location, status, personnel, description
    def addRecord(self):
        """新增資料功能"""
        self.updateAutoIncrementId(self.m_ui.date_time.date())

        record_id : str = self.generateId(self.m_ui.date_time.date())
        date : str = self.m_ui.date_time.dateTime().toString("yyyy/MM/dd hh:mm:ss")
        factory, location, status, personnel, description = self.extractData()

        if not factory or not location or not status or not personnel:
            QtWidgets.QMessageBox.warning(self, "警告", "請填寫所有必填資料。")
            return

        try:
            self.cursor.execute(
                "INSERT INTO Maintenance (id, Create_time, factory, location, status, personnel, description) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (record_id, date, factory, location, status, personnel, description),
            )
            self.m_db_connection.commit()
            new_record = [record_id, date, factory, location, status, personnel, description]
            self.m_records.append(new_record)
            self.updateTableView()
            self.m_ui.text_number.setText(record_id)
            QtWidgets.QMessageBox.information(self, "新增成功", f"成功新增編號：{record_id}")
        except Error as e:
            print(f"新增失敗：{e}")
            QtWidgets.QMessageBox.warning(self, "錯誤", f"新增失敗：{e}")

    def deleteRecord(self):
        """刪除資料功能"""
        selected_rows = self.m_ui.tableWidget_log.selectedItems()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "警告", "請選擇要刪除的記錄。")
            return

        row_index = selected_rows[0].row()
        record_id = self.m_records[row_index][0]

        try:
            self.cursor.execute("DELETE FROM Maintenance WHERE id = %s", (record_id,))
            self.m_db_connection.commit()
            del self.m_records[row_index]
            self.updateTableView()
            QtWidgets.QMessageBox.information(self, "刪除成功", f"已刪除編號：{record_id}")
        except Error as e:
            print(f"刪除失敗：{e}")
            QtWidgets.QMessageBox.warning(self, "錯誤", f"刪除失敗：{e}")

    def updateRecord(self):
        """更新資料功能"""
        selected_rows = self.m_ui.tableWidget_log.selectedItems()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "警告", "請選擇要更新的記錄。")
            return

        row_index = selected_rows[0].row()
        record_id = self.m_records[row_index][0]
        date = self.m_ui.date_time.dateTime().toString("yyyy/MM/dd hh:mm:ss")
        factory, location, status, personnel, description = self.extractData()

        if not factory or not location or not status or not personnel:
            QtWidgets.QMessageBox.warning(self, "警告", "請填寫所有必填資料。")
            return

        try:
            self.cursor.execute(
                "UPDATE Maintenance SET Create_time = %s, factory = %s, location = %s, "
                "status = %s, personnel = %s, description = %s WHERE id = %s",
                (date, factory, location, status, personnel, description, record_id),
            )
            self.m_db_connection.commit()
            updated_record = [record_id, date, factory, location, status, personnel, description]
            self.m_records[row_index] = updated_record
            self.updateTableView()
            QtWidgets.QMessageBox.information(self, "更新成功", f"編號：{record_id} 已更新成功")
        except Error as e:
            print(f"更新失敗：{e}")
            QtWidgets.QMessageBox.warning(self, "錯誤", f"更新失敗：{e}")

    def searchRecords(self):
        """查詢資料功能"""
        # 收集查詢條件
        search_id = self.m_ui.text_number.toPlainText().strip()
        selected_date = self.m_ui.date_time.date().toString("yyyy-MM-dd")  # 日期格式為 "yyyy-MM-dd"
        factory, location, status, personnel, description = self.extractData()

        try:
            # 動態生成 SQL 查詢語句
            query : str = "SELECT * FROM Maintenance WHERE 1=1"
            params : list = []

            # 編號條件
            if search_id:
                query += " AND id = %s"
                params.append(search_id)

            # 日期條件（忽略時間，只比對日期）
            if selected_date:
                query += " AND DATE(Create_time) = %s"
                params.append(selected_date)

            # 廠區條件
            if factory:
                query += " AND factory = %s"
                params.append(factory)

            # 機台位置（部分匹配）
            if location:
                query += " AND location LIKE %s"
                params.append(f"%{location}%")

            # 請修狀況條件
            if status:
                query += " AND status = %s"
                params.append(status)

            # 申報人員條件
            if personnel:
                query += " AND personnel = %s"
                params.append(personnel)

            # 請修狀況說明（部分匹配）
            if description:
                query += " AND description LIKE %s"
                params.append(f"%{description}%")

            # 執行查詢
            self.cursor.execute(query, tuple(params))
            filtered_records = self.cursor.fetchall()

            # 同步更新 self.m_records 並更新表格
            self.m_records = filtered_records
            self.updateTableView(filtered_records)

        except Error as e:
            print(f"查詢失敗：{e}")
            QtWidgets.QMessageBox.warning(self, "錯誤", f"查詢失敗：{e}")




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MaintenanceApp()
    window.show()
    sys.exit(app.exec())
