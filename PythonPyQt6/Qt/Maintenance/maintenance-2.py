from PyQt6 import QtWidgets, QtCore
from maintenance import Ui_MaintenanceWindow  # 導入生成的 UI 類
import datetime


class MaintenanceApp(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.m_ui = Ui_MaintenanceWindow()
        self.m_ui.setupUi(self)

        # 使用 QTableWidget 替換 QListView
        self.m_ui.listview_log = QtWidgets.QTableWidget(self.m_ui.centralwidget)
        self.m_ui.gridLayout.addWidget(self.m_ui.listview_log, 5, 1, 1, 6)

        # 設定表格標題與初始化
        self.m_ui.listview_log.setColumnCount(7)  # 7 列
        self.m_ui.listview_log.setHorizontalHeaderLabels(
            ["編號", "日期", "廠區", "機台使用位置", "請修狀況", "申報人員", "請修狀況說明"]
        )
        self.m_ui.listview_log.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.m_ui.listview_log.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 按鈕功能連結
        self.m_ui.button_add.clicked.connect(self.addRecord)
        self.m_ui.button_delete.clicked.connect(self.deleteRecord)
        self.m_ui.button_update.clicked.connect(self.updateRecord)
        self.m_ui.button_search.clicked.connect(self.searchRecords)
        self.m_ui.listview_log.itemSelectionChanged.connect(self.loadSelectedRecord)

        # 初始化資料
        self.m_records : list = []
        self.m_auto_increment_id : int = 1  # 編號起始值（為 0）
        self.m_ui.date_time.setDateTime(QtCore.QDateTime.currentDateTime())  # 預設當前時間

    def updateAutoIncrementId(self, date : QtCore.QDate) -> None :
        """根據選定日期更新自動遞增尾碼"""
        # 過濾出以選定日期開頭的記錄
        date_str : str = date.toString("yyyyMMdd")
        filtered_records : list = [record for record in self.m_records if record[0].startswith(date_str)]
        if filtered_records:
            # 找到選定日期中最大尾碼
            max_suffix : int = max(int(record[0].split('-')[1]) for record in filtered_records)
            self.m_auto_increment_id = max_suffix + 1
        else:
            self.m_auto_increment_id = 1

    def generateId(self, date : QtCore.QDate) -> str:
        """生成新的編號，格式為 [選定日期-編號]"""
        date_str = date.toString("yyyyMMdd")
        new_id : str = f"{date_str}-{self.m_auto_increment_id}"
        self.m_auto_increment_id += 1
        return new_id

    def updateTableView(self, records=None) -> None :
        """更新表格顯示"""
        if records is None:
            records : list = self.m_records

        self.m_ui.listview_log.setRowCount(len(records))
        for row_idx, record in enumerate(records):
            for col_idx, value in enumerate(record):
                self.m_ui.listview_log.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(value))

    def extractData(self) -> str :
        """提取表格中的資料"""
        factory = self.m_ui.combobox_factory.currentText()
        location = self.m_ui.text_location.toPlainText().strip()
        status = self.m_ui.combobox_status.currentText()
        personnel = self.m_ui.combobox_personnel.currentText()
        description = self.m_ui.text_description.toPlainText().strip()
        return factory, location, status, personnel, description
    
    def addRecord(self) -> None :
        """新增資料功能"""
        # 更新編號的遞增值（基於選定日期）
        self.updateAutoIncrementId(self.m_ui.date_time.date())

        # 收集資料
        record_id : str = self.generateId(self.m_ui.date_time.date())  # 生成編號
        date : str = self.m_ui.date_time.dateTime().toString("yyyy/MM/dd hh:mm:ss")
        factory, location, status, personnel, description = self.extractData()

        # 驗證必填資料
        if not factory or not location or not status or not personnel:
            QtWidgets.QMessageBox.warning(self, "警告", "請填寫所有必填資料。")
            return

        # 新增到記錄列表
        new_record : list = [record_id, date, factory, location, status, personnel, description]
        self.m_records.append(new_record)
        self.updateTableView()
        self.m_ui.text_number.setText(record_id)  # 更新編號顯示為新增的編號
        QtWidgets.QMessageBox.information(self, "新增成功", f"成功新增編號：{record_id}")

    def deleteRecord(self) -> None:
        """刪除資料功能"""
        selected_rows : list = self.m_ui.listview_log.selectedItems()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "警告", "請選擇要刪除的記錄。")
            return

        # 取得選定行索引並刪除
        row_index : int = selected_rows[0].row()
        record_id : str = self.m_records[row_index][0]
        del self.m_records[row_index]
        self.updateTableView()
        QtWidgets.QMessageBox.information(self, "刪除成功", f"已刪除編號：{record_id}")

    def updateRecord(self) -> None:
        """更新資料功能"""
        selected_rows : list = self.m_ui.listview_log.selectedItems()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "警告", "請選擇要更新的記錄。")
            return

        # 取得選定行索引
        row_index : int = selected_rows[0].row()

        # 保持選定的編號
        record_id : str = self.m_records[row_index][0]
        date : str = self.m_ui.date_time.dateTime().toString("yyyy/MM/dd hh:mm:ss")
        factory, location, status, personnel, description = self.extractData()

        # 驗證必填資料
        if not factory or not location or not status or not personnel:
            QtWidgets.QMessageBox.warning(self, "警告", "請填寫所有必填資料。")
            return

        # 更新記錄
        updated_record = [record_id, date, factory, location, status, personnel, description]
        self.m_records[row_index] = updated_record
        self.updateTableView()
        QtWidgets.QMessageBox.information(self, "更新成功", f"編號：{record_id} 已更新成功")

    def searchRecords(self) -> None :
        """查詢資料功能"""
        # 收集查詢條件
        search_id = self.m_ui.text_number.toPlainText().strip()
        selected_date = self.m_ui.date_time.date().toString("yyyy/MM/dd")
        factory, location, status, personnel, description = self.extractData()

        # 過濾資料
        filtered_records = [
            record for record in self.m_records
            if (not search_id or record[0] == search_id)
            and (not selected_date or record[1].startswith(selected_date))
            and (not factory or record[2] == factory)
            and (not location or record[3] == location)
            and (not status or record[4] == status)
            and (not personnel or record[5] == personnel)
            and (not description or record[6] == description)
        ]

        # 更新顯示
        self.updateTableView(filtered_records)

    def loadSelectedRecord(self) -> None :
        """選定資料並加載至輸入框（保持編號）。"""
        selected_rows = self.m_ui.listview_log.selectedItems()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        selected_record = self.m_records[row_index]

        self.m_ui.text_number.setText(selected_record[0])
        self.m_ui.date_time.setDateTime(QtCore.QDateTime.fromString(selected_record[1], "yyyy/MM/dd hh:mm:ss"))
        self.m_ui.combobox_factory.setCurrentText(selected_record[2])
        self.m_ui.text_location.setText(selected_record[3])
        self.m_ui.combobox_status.setCurrentText(selected_record[4])
        self.m_ui.combobox_personnel.setCurrentText(selected_record[5])
        self.m_ui.text_description.setText(selected_record[6])


if __name__ == "__main__" :
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MaintenanceApp()
    window.show()
    sys.exit(app.exec())
