import sys
from PySide6 import QtWidgets

from styles import load_theme

from pages.startPage import startPage
from pages.jsonPage import jsonPage
from pages.stockPage import stockPage
from pages.csvPage import csvPage
from pages.excelPage import excelPage


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analyzing Tool")
        self.resize(960, 640)
        self.setMinimumSize(800, 520)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.csv_page = csvPage(self.pageSwitch)
        self.excel_page = excelPage(self.pageSwitch)
        self.json_page = jsonPage(self.pageSwitch)

        self.start_page = startPage(
            self.pageSwitch,
            self.import_csv,
            self.import_excel,
            self.import_json,
        )

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.excel_page)
        self.stack.addWidget(self.json_page)
        self.stack.addWidget(stockPage(self.pageSwitch))
        self.stack.addWidget(self.csv_page)

    def import_csv(self):
        if self.csv_page.open_csv_file():
            self.stack.setCurrentWidget(self.csv_page)

    def import_excel(self):
        if self.excel_page.open_excel_file():
            self.stack.setCurrentWidget(self.excel_page)

    def import_json(self):
        if self.json_page.open_json_file():
            self.stack.setCurrentWidget(self.json_page)

    def pageSwitch(self, index):
        self.stack.setCurrentIndex(index)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    load_theme(app)

    ikkuna = mainWindow()
    ikkuna.show()
    sys.exit(app.exec())