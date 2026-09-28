"""元素・同位体・物理定数を検索する常設パネル。"""
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from .data import (
    CONSTANT_COLUMNS, ELEMENT_COLUMNS, ISOTOPE_COLUMNS, all_elements, all_isotopes,
    common_constants, find_constant, find_element, find_isotope, japanese_constant_name,
)

MODE_ELEMENT = "元素"
MODE_ISOTOPE = "同位体"
MODE_CONSTANT = "物理定数"

_PLACEHOLDERS = {
    MODE_ELEMENT: "元素記号・原子番号・英語名・日本語名(例: Fe、26、鉄)",
    MODE_ISOTOPE: "元素か核種(例: Fe、Fe-56、56Fe、鉄56)",
    MODE_CONSTANT: "定数名(例: 光速、Boltzmann、electron mass)",
}


class _CopyableTable(QTableWidget):
    """選択したセルを Ctrl+C / 右クリックでタブ区切りのテキストとしてコピーできる表。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def event(self, event):
        # 本体のメニューにも Ctrl+C があるので、フォーカス中は表のコピーを優先させる
        if event.type() == QEvent.Type.ShortcutOverride and event.matches(QKeySequence.StandardKey.Copy):
            event.accept()
            return True
        return super().event(event)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
            return
        super().keyPressEvent(event)

    def selected_text(self):
        indexes = self.selectedIndexes()
        if not indexes:
            return ""
        rows = sorted({i.row() for i in indexes})
        cols = sorted({i.column() for i in indexes})
        selected = {(i.row(), i.column()) for i in indexes}
        lines = []
        for r in rows:
            cells = []
            for c in cols:
                item = self.item(r, c)
                cells.append(item.text() if item is not None and (r, c) in selected else "")
            lines.append("\t".join(cells))
        return "\n".join(lines)

    def copy_selection(self):
        text = self.selected_text()
        if text:
            QGuiApplication.clipboard().setText(text)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        action = QAction("コピー", menu)
        action.setEnabled(bool(self.selectedIndexes()))
        action.triggered.connect(self.copy_selection)
        menu.addAction(action)
        menu.exec(self.viewport().mapToGlobal(pos))


class ElementConstantsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        search_row = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([MODE_ELEMENT, MODE_ISOTOPE, MODE_CONSTANT])
        self.mode_combo.currentTextChanged.connect(self._on_search_changed)
        search_row.addWidget(self.mode_combo)

        self.search_edit = QLineEdit()
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self.search_edit, 1)
        layout.addLayout(search_row)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.result_table = _CopyableTable()
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.result_table)

        self._on_search_changed()

    def show_isotopes_of(self, symbol):
        self.search_edit.blockSignals(True)
        self.search_edit.setText(symbol)
        self.search_edit.blockSignals(False)
        self.mode_combo.setCurrentText(MODE_ISOTOPE)
        self._on_search_changed()

    def _on_cell_double_clicked(self, row, _column):
        if self.mode_combo.currentText() == MODE_ELEMENT:
            self.show_isotopes_of(self.result_table.item(row, 1).text())

    def _on_search_changed(self, _text=None):
        mode = self.mode_combo.currentText()
        query = self.search_edit.text().strip()
        self.search_edit.setPlaceholderText(_PLACEHOLDERS[mode])

        if mode == MODE_ELEMENT:
            rows = find_element(query) if query else all_elements()
            self._populate_table(ELEMENT_COLUMNS, rows)
            hint = "ダブルクリックで同位体を表示"
            status = f"全 {len(rows)} 元素。{hint}" if not query else f"{len(rows)} 件。{hint}"
        elif mode == MODE_ISOTOPE:
            rows = find_isotope(query) if query else all_isotopes()
            self._populate_table(ISOTOPE_COLUMNS, rows)
            status = f"全 {len(rows)} 核種" if not query else f"{len(rows)} 件"
            status += "(天然存在比が「—」の核種は天然に存在しない代表的な長寿命核種)"
        else:
            rows = find_constant(query) if query else common_constants()
            display = [(self._constant_label(r[0]),) + tuple(r[1:]) for r in rows]
            self._populate_table(CONSTANT_COLUMNS, display)
            status = "よく使う定数。英語名でも全 CODATA 値から探せます" if not query else f"{len(rows)} 件"

        if query and not rows:
            status = "該当なし"
        self.status_label.setText(status)

    @staticmethod
    def _constant_label(name):
        japanese = japanese_constant_name(name)
        return f"{japanese}({name})" if japanese else name

    def _populate_table(self, columns, rows):
        table = self.result_table
        table.setUpdatesEnabled(False)
        table.clearContents()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(len(rows))
        for row_index, row_values in enumerate(rows):
            for col_index, value in enumerate(row_values):
                table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        table.horizontalHeader().resizeSections(QHeaderView.ResizeMode.ResizeToContents)
        table.setUpdatesEnabled(True)
