import csv
import io
import os

from PySide6 import QtCore, QtWidgets


class csvPage(QtWidgets.QWidget):
    def __init__(self, pageSwitchFunction):
        super().__init__()
        self.pageSwitch = pageSwitchFunction

        self.back_button = QtWidgets.QPushButton("← Takaisin")
        self.back_button.setObjectName("backButton")
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.clicked.connect(lambda: self.pageSwitch(0))

        self.file_label = QtWidgets.QLabel("Ei tiedostoa valittu")
        self.file_label.setProperty("role", "fileLabel")

        self.table = QtWidgets.QTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        top = QtWidgets.QHBoxLayout()
        top.setContentsMargins(12, 12, 12, 4)
        top.addWidget(self.back_button)
        top.addSpacing(12)
        top.addWidget(self.file_label, 1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.addLayout(top)
        layout.addWidget(self.table, 1)

    def open_csv_file(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Avaa CSV-tiedosto",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        if not filepath:
            return False
        return self.load_csv(filepath)

    def load_csv(self, filepath):
        try:
            with open(filepath, "rb") as f:
                raw = f.read()
        except OSError:
            self.file_label.setText("Tiedostoa ei voitu avata")
            return False

        text = self._decode(raw)
        if text is None:
            self.file_label.setText("Tiedoston merkistöä ei voitu lukea")
            return False

        rows = self._parse_rows(text)
        if not rows:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.file_label.setText(f"{os.path.basename(filepath)} — tyhjä tiedosto")
            return True

        headers = rows[0]
        data = rows[1:]
        column_count = max((len(row) for row in rows), default=0)
        headers = headers + [""] * (column_count - len(headers))

        self.table.clear()
        self.table.setColumnCount(column_count)
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(headers)

        for row_index, row in enumerate(data):
            for column_index in range(column_count):
                value = row[column_index] if column_index < len(row) else ""
                self.table.setItem(
                    row_index,
                    column_index,
                    QtWidgets.QTableWidgetItem(value),
                )

        self.table.resizeColumnsToContents()
        self.file_label.setText(
            f"{os.path.basename(filepath)} — {len(data)} riviä"
        )
        return True

    def _decode(self, raw):
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return None

    def _parse_rows(self, text):
        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        return list(csv.reader(io.StringIO(text), dialect))
