import os
from PySide6 import QtWidgets


def load_theme(app: QtWidgets.QApplication) -> None:
    """Load the global dark theme from theme.qss and apply it to the app."""
    base_dir = os.path.dirname(__file__)
    qss_path = os.path.join(base_dir, "theme.qss")

    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    except OSError:
        # Fallback: minimal dark theme if qss file is missing
        app.setStyleSheet(
            "QWidget { background-color: #1c1c1e; color: #f4f4f5; }"
        )


def apply_button_style(btn: QtWidgets.QPushButton, variant: str = "default") -> None:
    """Optional helper for special button variants (keeps Python side minimal)."""
    if variant == "back":
        btn.setProperty("class", "backButton")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
    # Other variants can be added later without bloating pages
