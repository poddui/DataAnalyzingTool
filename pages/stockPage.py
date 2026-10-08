import datetime
import os

import requests
from dotenv import load_dotenv
from PySide6 import QtCore, QtWidgets

# .env lives in the project root, one level above pages/
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
API_KEY = os.getenv("FINNHUB_API_KEY")
HEADERS = {"X-Finnhub-Token": API_KEY}
SEARCH_URL = "https://finnhub.io/api/v1/search"
QUOTE_URL = "https://finnhub.io/api/v1/quote"
PROFILE_URL = "https://finnhub.io/api/v1/stock/profile2"
REQUEST_TIMEOUT = 12


def format_price(value, currency=""):
    if value is None:
        return "—"
    number = f"{value:,.2f}".replace(",", " ")
    return f"{number} {currency}".strip()


def format_change(delta, percent):
    if delta is None or percent is None:
        return "—"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.2f}  ({sign}{percent:.2f} %)"


def format_compact(millions):
    if millions is None:
        return "—"
    if millions >= 1_000_000:
        return f"{millions / 1_000_000:.2f} T"
    if millions >= 1_000:
        return f"{millions / 1_000:.2f} mrd."
    return f"{millions:.1f} milj."


def format_listed(value):
    if not value:
        return "—"
    try:
        return datetime.date.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError:
        return value


def change_color(percent):
    if percent is None or percent == 0:
        return "#71717a"
    return "#22c55e" if percent > 0 else "#ef4444"


class _ResultRow(QtWidgets.QWidget):
    def __init__(self, symbol, name, kind):
        super().__init__()
        self.setObjectName("resultRow")
        self.setAutoFillBackground(False)

        symbol_label = QtWidgets.QLabel(symbol)
        symbol_label.setObjectName("resultSymbol")

        kind_label = QtWidgets.QLabel(kind or "")
        kind_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        kind_label.setObjectName("resultKind")

        name_label = QtWidgets.QLabel(name or "—")
        name_label.setObjectName("resultName")

        top = QtWidgets.QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)
        top.addWidget(symbol_label)
        top.addWidget(kind_label, 1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(top)
        layout.addWidget(name_label)


class stockPage(QtWidgets.QWidget):
    def __init__(self, pageSwitchFunction):
        super().__init__()
        self.pageSwitch = pageSwitchFunction

        self.back_button = QtWidgets.QPushButton("← Takaisin")
        self.back_button.setObjectName("backButton")
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.clicked.connect(lambda: self.pageSwitch(0))

        self.searchbar = QtWidgets.QLineEdit()
        self.searchbar.setObjectName("stockSearch")
        self.searchbar.setPlaceholderText("Hae osake nimellä tai tickerillä...")
        self.searchbar.returnPressed.connect(self.search_results)

        self.search_button = QtWidgets.QPushButton("Hae")
        self.search_button.setObjectName("searchButton")
        self.search_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.search_button.setAutoDefault(False)
        self.search_button.setDefault(False)
        self.search_button.clicked.connect(self.search_results)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setProperty("role", "status")

        self.result_list = QtWidgets.QListWidget()
        self.result_list.setObjectName("resultList")
        self.result_list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.result_list.setFrameShadow(QtWidgets.QFrame.Plain)
        self.result_list.setSelectionRectVisible(False)
        self.result_list.setAlternatingRowColors(False)
        self.result_list.setSpacing(0)
        self.result_list.setUniformItemSizes(True)
        self.result_list.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.result_list.setContentsMargins(0, 0, 0, 0)
        self.result_list.itemClicked.connect(self.on_item_selected)
        self.result_list.setMinimumWidth(180)

        self.detail = self._build_detail()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.result_list)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        top = QtWidgets.QHBoxLayout()
        top.setContentsMargins(12, 12, 12, 4)
        top.addWidget(self.back_button)
        top.addSpacing(10)
        top.addWidget(self.searchbar, 1)
        top.addSpacing(8)
        top.addWidget(self.search_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.addLayout(top)
        layout.addWidget(self.status_label)
        layout.addWidget(splitter, 1)

        self._show_placeholder("Hae osaketta nimellä tai tickerillä.")

    def _build_detail(self):
        card = QtWidgets.QFrame()
        card.setObjectName("quoteCard")
        # Styling provided by styles/theme.qss via #quoteCard selector

        self.placeholder = QtWidgets.QLabel()
        self.placeholder.setWordWrap(True)
        self.placeholder.setAlignment(QtCore.Qt.AlignCenter)

        self.symbol_label = QtWidgets.QLabel()
        self.symbol_label.setObjectName("stockSymbol")

        self.name_label = QtWidgets.QLabel()
        self.name_label.setWordWrap(True)
        self.name_label.setObjectName("stockName")

        self.meta_label = QtWidgets.QLabel()
        self.meta_label.setWordWrap(True)
        self.meta_label.setObjectName("stockMeta")

        self.price_label = QtWidgets.QLabel()
        self.price_label.setObjectName("stockPrice")

        self.change_label = QtWidgets.QLabel()
        self.change_label.setObjectName("stockChange")

        self.metric_labels = {}
        metrics = QtWidgets.QGridLayout()
        metrics.setHorizontalSpacing(24)
        metrics.setVerticalSpacing(8)
        fields = [
            ("open", "Avaus"),
            ("high", "Päivän ylin"),
            ("low", "Päivän alin"),
            ("previous", "Edellinen sulku"),
            ("market_cap", "Markkina-arvo"),
            ("shares", "Osakkeita"),
            ("ipo", "Listattu"),
            ("updated", "Päivitetty"),
        ]
        for index, (key, title) in enumerate(fields):
            title_label = QtWidgets.QLabel(title)
            title_label.setObjectName("metricTitle")
            value_label = QtWidgets.QLabel("—")
            value_label.setObjectName("metricValue")
            self.metric_labels[key] = value_label
            column = 0 if index % 2 == 0 else 1
            row = (index // 2) * 2
            metrics.addWidget(title_label, row, column)
            metrics.addWidget(value_label, row + 1, column)

        self.web_label = QtWidgets.QLabel()
        self.web_label.setOpenExternalLinks(True)
        self.web_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.web_label.setObjectName("stockWeb")

        self.detail_body = QtWidgets.QWidget()
        body = QtWidgets.QVBoxLayout(self.detail_body)
        body.setContentsMargins(20, 18, 20, 18)
        body.addWidget(self.symbol_label)
        body.addWidget(self.name_label)
        body.addWidget(self.meta_label)
        body.addSpacing(8)
        body.addWidget(self.price_label)
        body.addWidget(self.change_label)
        body.addSpacing(14)
        body.addLayout(metrics)
        body.addSpacing(10)
        body.addWidget(self.web_label)
        body.addStretch(1)

        stack = QtWidgets.QVBoxLayout(card)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.addWidget(self.placeholder)
        stack.addWidget(self.detail_body)
        return card

    def search_results(self):
        query = self.searchbar.text().strip()
        if not query:
            self.status_label.setText("Kirjoita hakusana.")
            return
        if not API_KEY:
            self.status_label.setText("FINNHUB_API_KEY puuttuu projektin juuren .env-tiedostosta.")
            return

        self.status_label.setText("Haetaan...")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            response = requests.get(
                SEARCH_URL,
                headers=HEADERS,
                params={"q": query},
                timeout=REQUEST_TIMEOUT,
            )
            data = response.json()
        except (requests.RequestException, ValueError):
            self.status_label.setText("Haku epäonnistui. Yritä uudelleen.")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if response.status_code >= 300:
            self.status_label.setText("Haku epäonnistui.")
            return

        results = data.get("result") or []
        self.result_list.clear()
        if not results:
            self.status_label.setText("Ei tuloksia.")
            self._show_placeholder("Osaketta ei löytynyt.")
            return

        for item in results:
            self._add_result(item)

        count = len(results)
        self.status_label.setText(
            "1 tulos" if count == 1 else f"{count} tulosta"
        )
        self.result_list.setCurrentRow(0)
        self.on_item_selected(self.result_list.item(0))

    def _add_result(self, item):
        row = QtWidgets.QListWidgetItem()
        row.setData(QtCore.Qt.UserRole, item)
        widget = _ResultRow(
            item.get("symbol") or item.get("displaySymbol") or "",
            item.get("description") or "",
            item.get("type") or "",
        )
        row.setSizeHint(widget.sizeHint())
        self.result_list.addItem(row)
        self.result_list.setItemWidget(row, widget)

    def on_item_selected(self, item):
        stock = item.data(QtCore.Qt.UserRole) if item else None
        if not stock:
            return

        ticker = stock.get("symbol") or stock.get("displaySymbol")
        if not ticker:
            self._show_placeholder("Osakkeelta puuttuu ticker.")
            return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            quote, profile = self._fetch_details(ticker)
        except requests.RequestException:
            self._show_placeholder("Hintatietoja ei saatu ladattua.")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if quote is None:
            self._show_placeholder("Hintatietoja ei saatu ladattua.")
            return
        self._apply_quote(stock, quote, profile or {})

    def _fetch_details(self, ticker):
        quote_response = requests.get(
            QUOTE_URL,
            headers=HEADERS,
            params={"symbol": ticker},
            timeout=REQUEST_TIMEOUT,
        )
        if quote_response.status_code >= 300:
            return None, None
        try:
            quote = quote_response.json()
        except ValueError:
            return None, None

        profile = {}
        try:
            profile_response = requests.get(
                PROFILE_URL,
                headers=HEADERS,
                params={"symbol": ticker},
                timeout=REQUEST_TIMEOUT,
            )
            if profile_response.status_code < 300:
                profile = profile_response.json() or {}
        except (requests.RequestException, ValueError):
            profile = {}
        return quote, profile

    def _apply_quote(self, stock, quote, profile):
        ticker = (
            profile.get("ticker")
            or stock.get("displaySymbol")
            or stock.get("symbol")
            or ""
        )
        name = profile.get("name") or stock.get("description") or ticker
        currency = profile.get("currency") or ""
        price = quote.get("c")
        delta = quote.get("d")
        percent = quote.get("dp")
        timestamp = quote.get("t")

        no_quote = not price and not timestamp
        if no_quote:
            self._show_placeholder(f"Ei hintatietoja tunnukselle {ticker}.")
            return

        meta_parts = [
            part
            for part in (
                profile.get("exchange"),
                profile.get("finnhubIndustry"),
                profile.get("country"),
                stock.get("type"),
            )
            if part
        ]

        self.placeholder.hide()
        self.detail_body.show()
        self.symbol_label.setText(ticker)
        self.name_label.setText(name)
        self.meta_label.setText(" · ".join(meta_parts))
        self.price_label.setText(format_price(price, currency))
        self.change_label.setText(format_change(delta, percent))
        # Dynamic color handled via property + QSS
        if percent is None or percent == 0:
            self.change_label.setProperty("change", "neutral")
        elif percent > 0:
            self.change_label.setProperty("change", "positive")
        else:
            self.change_label.setProperty("change", "negative")
        self.change_label.style().unpolish(self.change_label)
        self.change_label.style().polish(self.change_label)

        updated = "—"
        if timestamp:
            updated = datetime.datetime.fromtimestamp(timestamp).strftime(
                "%H:%M %d.%m.%Y"
            )

        values = {
            "open": format_price(quote.get("o"), currency),
            "high": format_price(quote.get("h"), currency),
            "low": format_price(quote.get("l"), currency),
            "previous": format_price(quote.get("pc"), currency),
            "market_cap": self._with_currency(
                format_compact(profile.get("marketCapitalization")), currency
            ),
            "shares": format_compact(profile.get("shareOutstanding")),
            "ipo": format_listed(profile.get("ipo")),
            "updated": updated,
        }
        for key, value in values.items():
            self.metric_labels[key].setText(value)

        url = profile.get("weburl")
        if url:
            self.web_label.setText(f'<a href="{url}">{url}</a>')
        else:
            self.web_label.clear()

    def _with_currency(self, value, currency):
        if value == "—" or not currency:
            return value
        return f"{value} {currency}"

    def _show_placeholder(self, text):
        self.placeholder.setText(text)
        self.placeholder.show()
        self.detail_body.hide()
