import json
import os

from PySide6 import QtCore, QtGui, QtWidgets


class jsonPage(QtWidgets.QWidget):
    def __init__(self, pageSwitchFunction):
        super().__init__()
        self.pageSwitch = pageSwitchFunction

        self.back_button = QtWidgets.QPushButton("← Takaisin")
        self.back_button.setObjectName("backButton")
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.clicked.connect(lambda: self.pageSwitch(0))

        self.file_label = QtWidgets.QLabel("Ei tiedostoa valittu")
        self.file_label.setProperty("role", "fileLabel")

        self.text_editor = QtWidgets.QTextEdit()
        self.text_editor.setReadOnly(True)
        self.text_editor.setFont(
            QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        )

        top = QtWidgets.QHBoxLayout()
        top.setContentsMargins(12, 12, 12, 4)
        top.addWidget(self.back_button)
        top.addSpacing(12)
        top.addWidget(self.file_label, 1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.addLayout(top)
        layout.addWidget(self.text_editor, 1)

    def open_json_file(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Avaa JSON-tiedosto",
            "",
            "JSON Files (*.json)",
        )
        if not filepath:
            return False
        return self.load_json(filepath)

    def load_json(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except OSError:
            self.file_label.setText("Tiedostoa ei voitu avata")
            return False
        except json.JSONDecodeError:
            self.file_label.setText(
                f"{os.path.basename(filepath)} — virheellinen JSON"
            )
            self.text_editor.setPlainText("Virheellinen JSON-tiedosto")
            return True
        self.show_json(data, filepath)
        return True

    def show_json(self, data, filepath=None):
        formatted = json.dumps(data, indent=4, ensure_ascii=False)
        self.text_editor.setPlainText(formatted)
        name = os.path.basename(filepath) if filepath else "JSON"
        self.file_label.setText(f"{name} — {self._summary(data)}")

    def _summary(self, data):
        if isinstance(data, dict):
            count = len(data)
            return "1 avain" if count == 1 else f"{count} avainta"
        if isinstance(data, list):
            count = len(data)
            return "1 alkio" if count == 1 else f"{count} alkiota"
        return type(data).__name__