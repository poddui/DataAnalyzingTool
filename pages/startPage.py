from PySide6 import QtCore, QtWidgets


class startPage(QtWidgets.QWidget):
    def __init__(
        self,
        pageSwitchFunction,
        importCsvFunction=None,
        importExcelFunction=None,
        importJsonFunction=None,
    ):
        super().__init__()
        self.pageSwitch = pageSwitchFunction

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(60, 50, 60, 50)
        main_layout.setSpacing(28)

        title = QtWidgets.QLabel("Data Analyzing Tool")
        title.setObjectName("startTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel("Import, explore and analyze your data")
        subtitle.setObjectName("startSubtitle")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        btn_csv = self._create_action_button("Import CSV")
        btn_excel = self._create_action_button("Import Excel")
        btn_json = self._create_action_button("Import JSON")
        btn_stock = self._create_action_button("Search Stocks")

        grid.addWidget(btn_csv, 0, 0)
        grid.addWidget(btn_excel, 0, 1)
        grid.addWidget(btn_json, 1, 0)
        grid.addWidget(btn_stock, 1, 1)

        grid_wrapper = QtWidgets.QWidget()
        grid_wrapper_layout = QtWidgets.QHBoxLayout(grid_wrapper)
        grid_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        grid_wrapper_layout.addStretch()
        grid_wrapper_layout.addLayout(grid)
        grid_wrapper_layout.addStretch()

        footer = QtWidgets.QLabel("Choose a data source to begin")
        footer.setObjectName("startFooter")
        footer.setAlignment(QtCore.Qt.AlignCenter)

        main_layout.addStretch(1)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(16)
        main_layout.addWidget(grid_wrapper)
        main_layout.addSpacing(20)
        main_layout.addWidget(footer)
        main_layout.addStretch(2)

        btn_csv.clicked.connect(importCsvFunction or (lambda: self.pageSwitch(4)))
        btn_excel.clicked.connect(importExcelFunction or (lambda: self.pageSwitch(1)))
        btn_json.clicked.connect(importJsonFunction or (lambda: self.pageSwitch(2)))
        btn_stock.clicked.connect(lambda: self.pageSwitch(3))

    def _create_action_button(self, text):
        btn = QtWidgets.QPushButton()
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setProperty("actionButton", "true")
        btn.setMinimumSize(128, 52)

        layout = QtWidgets.QVBoxLayout(btn)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        text_label.setObjectName("actionText")

        layout.addWidget(text_label)

        return btn
