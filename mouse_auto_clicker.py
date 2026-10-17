"""
Auto Clicker — PyQt6 自動滑鼠連點工具

需要套件：
    python -m pip install pyautogui pynput PyQt6
"""

import sys
import threading

import pyautogui
from pynput import keyboard

from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

# 關閉 PyAutoGUI 預設的額外暫停
pyautogui.PAUSE = 0

# 緊急停止：把滑鼠移到主螢幕左上角會讓 PyAutoGUI 拋出例外並停止
pyautogui.FAILSAFE = True


# =========================================================
# 全域快捷鍵設定
# =========================================================

HOTKEY_DISPLAY = (
    [f"Ctrl + {chr(i).upper()}" for i in range(ord("a"), ord("z") + 1)]
    + [f"F{i}" for i in range(1, 13)]
)

HOTKEY_PYNPUT = (
    [f"<ctrl>+{chr(i)}" for i in range(ord("a"), ord("z") + 1)]
    + [f"<f{i}>" for i in range(1, 13)]
)

DISPLAY_TO_HOTKEY = dict(zip(HOTKEY_DISPLAY, HOTKEY_PYNPUT))


# =========================================================
# 介面文字（中英文）
# =========================================================

TEXTS = {
    "繁體中文": {
        "subtitle": "自動滑鼠連點工具",
        "language": "語言",
        "section_click": "點擊設定",
        "mouse": "滑鼠按鍵",
        "left": "左鍵",
        "right": "右鍵",
        "action": "點擊方式",
        "single": "單擊",
        "double": "雙擊",
        "interval": "點擊間隔",
        "hours": "時",
        "minutes": "分",
        "seconds": "秒",
        "tenth": "1/10 秒",
        "hundredth": "1/100 秒",
        "interval_summary": "每 {:.2f} 秒點擊一次",
        "interval_zero": "無間隔（最快速度）",
        "count": "點擊次數",
        "infinite": "無限點擊",
        "section_hotkey": "全域快捷鍵",
        "start_hotkey": "啟動",
        "stop_hotkey": "停止",
        "status": "狀態",
        "status_ready": "就緒",
        "status_running": "執行中",
        "status_stopping": "停止中…",
        "status_error": "發生錯誤",
        "hotkey_error": "快捷鍵無法啟用：{}",
        "hint": "緊急停止：將滑鼠快速移到主螢幕左上角",
    },
    "English": {
        "subtitle": "Automatic mouse clicker",
        "language": "Language",
        "section_click": "Click settings",
        "mouse": "Mouse button",
        "left": "Left click",
        "right": "Right click",
        "action": "Mouse action",
        "single": "Single click",
        "double": "Double click",
        "interval": "Interval",
        "hours": "Hours",
        "minutes": "Min",
        "seconds": "Sec",
        "tenth": "1/10 s",
        "hundredth": "1/100 s",
        "interval_summary": "One click every {:.2f} s",
        "interval_zero": "No delay (max speed)",
        "count": "Click count",
        "infinite": "Infinite",
        "section_hotkey": "Global hotkeys",
        "start_hotkey": "Start",
        "stop_hotkey": "Stop",
        "status": "Status",
        "status_ready": "Ready",
        "status_running": "Running",
        "status_stopping": "Stopping…",
        "status_error": "Error",
        "hotkey_error": "Hotkey unavailable: {}",
        "hint": "Emergency stop: move the mouse to the top-left corner",
    },
}


# =========================================================
# 樣式表
# =========================================================

STYLE_SHEET = """
QWidget#root {
    background-color: #f1f5f9;
}

QWidget {
    color: #1e293b;
    font-size: 13px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#subtitle, QLabel#muted {
    color: #64748b;
}

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    padding-bottom: 2px;
}

QLabel#fieldLabel {
    color: #334155;
    font-weight: 600;
}

QLabel#caption {
    color: #94a3b8;
    font-size: 11px;
}

QLabel#summary {
    color: #2563eb;
    font-size: 12px;
}

QLabel#hint {
    color: #94a3b8;
    font-size: 11px;
}

QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 6px 8px;
    min-height: 20px;
}

QComboBox:hover, QSpinBox:hover {
    border-color: #94a3b8;
}

QComboBox:focus, QSpinBox:focus {
    border-color: #2563eb;
}

QComboBox:disabled, QSpinBox:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    selection-background-color: #dbeafe;
    selection-color: #1e3a8a;
    outline: 0;
}

QToolButton#stepButton {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    font-size: 8px;
    padding: 0;
}

QToolButton#stepButton:hover {
    background-color: #dbeafe;
    color: #2563eb;
    border-color: #93c5fd;
}

QToolButton#stepButton:pressed {
    background-color: #bfdbfe;
}

QToolButton#stepButton:disabled {
    background-color: #f8fafc;
    color: #cbd5e1;
    border-color: #e2e8f0;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox:disabled {
    color: #94a3b8;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #94a3b8;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

QLabel#statusPill {
    border-radius: 12px;
    padding: 5px 14px;
    font-weight: 700;
}

QLabel#statusPill[state="ready"] {
    background-color: #e2e8f0;
    color: #475569;
}

QLabel#statusPill[state="running"] {
    background-color: #dcfce7;
    color: #15803d;
}

QLabel#statusPill[state="stopping"] {
    background-color: #fef3c7;
    color: #b45309;
}

QLabel#statusPill[state="error"] {
    background-color: #fee2e2;
    color: #b91c1c;
}

QLabel#statusDetail {
    color: #b91c1c;
    font-size: 11px;
}

QPushButton {
    border-radius: 8px;
    padding: 10px 0;
    font-size: 14px;
    font-weight: 700;
    min-height: 20px;
}

QPushButton#startButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
}

QPushButton#startButton:hover {
    background-color: #1d4ed8;
}

QPushButton#stopButton {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
}

QPushButton#stopButton:hover {
    background-color: #b91c1c;
}

QPushButton#exitButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}

QPushButton#exitButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
}

QPushButton:disabled,
QPushButton#startButton:disabled,
QPushButton#stopButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border: none;
}
"""


# =========================================================
# 全域快捷鍵訊號橋接
# 避免直接從鍵盤監聽執行緒操作 GUI
# =========================================================

class HotkeyBridge(QObject):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()


# =========================================================
# 點擊執行緒
# =========================================================

class ClickWorker(QThread):
    error_occurred = pyqtSignal(str)

    def __init__(self, button, clicks, interval, click_count):
        super().__init__()

        self.button = button

        # clicks = 1 單擊，clicks = 2 雙擊
        self.clicks = clicks
        self.interval = max(0.0, interval)

        # click_count = 0 代表無限點擊
        self.click_count = click_count

        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        count = 0

        try:
            while not self.stop_event.is_set():
                pyautogui.click(
                    button=self.button,
                    clicks=self.clicks,
                    interval=0.0,
                )
                count += 1

                # 達到指定次數後停止
                if self.click_count > 0 and count >= self.click_count:
                    break

                # 可被 STOP 中斷的等待
                if self.stop_event.wait(self.interval):
                    break

        except Exception as exc:
            self.error_occurred.emit(str(exc))


# =========================================================
# 主視窗
# =========================================================

class AutoClicker(QWidget):

    def __init__(self):
        super().__init__()

        self.worker = None
        self.listener = None
        self.closing = False

        self.current_language = "繁體中文"
        self.status_state = "ready"
        self.status_detail = ""

        self.last_start_hotkey = "F2"
        self.last_stop_hotkey = "F3"

        # 時間欄位的上下箭頭按鈕（執行中會一起鎖定）
        self.step_buttons = []

        self.bridge = HotkeyBridge()
        self.bridge.start_requested.connect(self.start_clicking)
        self.bridge.stop_requested.connect(self.stop_clicking)

        self.setObjectName("root")
        self.setWindowTitle("Auto Clicker")
        self.setMinimumWidth(480)
        self.setStyleSheet(STYLE_SHEET)

        self.build_ui()
        self.update_language()
        self.set_running_ui(False)
        self.start_hotkey_listener()

        self.adjustSize()

    # -----------------------------------------------------
    # 小工具
    # -----------------------------------------------------

    def t(self, key):
        return TEXTS[self.current_language][key]

    @staticmethod
    def label(object_name="fieldLabel", text=""):
        widget = QLabel(text)
        widget.setObjectName(object_name)
        return widget

    @staticmethod
    def make_card():
        card = QFrame()
        card.setObjectName("card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(12)

        title = QLabel()
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        return card, layout, title

    def make_time_field(self, maximum, value=0):
        spin = QSpinBox()
        spin.setRange(0, maximum)
        spin.setValue(value)
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setMinimumWidth(40)
        spin.valueChanged.connect(self.update_interval_summary)

        # 自訂上下箭頭按鈕（按住可連續調整）
        up_button = QToolButton()
        up_button.setText("▲")
        down_button = QToolButton()
        down_button.setText("▼")

        for step_button in (up_button, down_button):
            step_button.setObjectName("stepButton")
            step_button.setFixedSize(20, 16)
            step_button.setAutoRepeat(True)
            step_button.setAutoRepeatDelay(350)
            step_button.setAutoRepeatInterval(60)
            step_button.setCursor(Qt.CursorShape.PointingHandCursor)
            step_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.step_buttons.append(step_button)

        up_button.clicked.connect(spin.stepUp)
        down_button.clicked.connect(spin.stepDown)

        arrows = QVBoxLayout()
        arrows.setSpacing(2)
        arrows.addWidget(up_button)
        arrows.addWidget(down_button)

        field = QHBoxLayout()
        field.setSpacing(3)
        field.addWidget(spin, 1)
        field.addLayout(arrows)

        caption = self.label("caption")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        box = QVBoxLayout()
        box.setSpacing(4)
        box.addLayout(field)
        box.addWidget(caption)

        return spin, caption, box

    # -----------------------------------------------------
    # 建立 GUI
    # -----------------------------------------------------

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)

        # ---------- 標題列 ----------
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        title = self.label("title", "Auto Clicker")
        self.subtitle_label = self.label("subtitle")

        title_box.addWidget(title)
        title_box.addWidget(self.subtitle_label)

        self.language_label = self.label("muted")
        self.language_combo = QComboBox()
        self.language_combo.addItems(list(TEXTS.keys()))
        self.language_combo.currentTextChanged.connect(self.change_language)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self.language_label)
        header.addWidget(self.language_combo)

        root.addLayout(header)

        # ---------- 點擊設定卡片 ----------
        click_card, click_layout, self.click_title = self.make_card()

        form = QGridLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(14)
        form.setColumnStretch(1, 1)
        click_layout.addLayout(form)

        # 滑鼠按鍵
        self.mouse_label = self.label()
        self.mouse_combo = QComboBox()
        self.mouse_combo.addItem("", "left")
        self.mouse_combo.addItem("", "right")

        form.addWidget(self.mouse_label, 0, 0)
        form.addWidget(self.mouse_combo, 0, 1)

        # 點擊方式（單擊／雙擊）
        self.action_label = self.label()
        self.action_combo = QComboBox()
        self.action_combo.addItem("", 1)
        self.action_combo.addItem("", 2)

        form.addWidget(self.action_label, 1, 0)
        form.addWidget(self.action_combo, 1, 1)

        # 點擊間隔（時／分／秒／十分之一秒／百分之一秒）
        self.interval_label = self.label()

        self.hours_spin, self.hours_caption, hours_box = \
            self.make_time_field(999)
        self.minutes_spin, self.minutes_caption, minutes_box = \
            self.make_time_field(59)
        self.seconds_spin, self.seconds_caption, seconds_box = \
            self.make_time_field(59)
        self.tenth_spin, self.tenth_caption, tenth_box = \
            self.make_time_field(9, value=1)
        self.hundredth_spin, self.hundredth_caption, hundredth_box = \
            self.make_time_field(9)

        time_row = QHBoxLayout()
        time_row.setSpacing(8)
        for box in (hours_box, minutes_box, seconds_box,
                    tenth_box, hundredth_box):
            time_row.addLayout(box)

        self.interval_summary = self.label("summary")

        time_column = QVBoxLayout()
        time_column.setSpacing(6)
        time_column.addLayout(time_row)
        time_column.addWidget(self.interval_summary)

        interval_label_box = QVBoxLayout()
        interval_label_box.setContentsMargins(0, 8, 0, 0)
        interval_label_box.addWidget(self.interval_label)
        interval_label_box.addStretch()

        form.addLayout(interval_label_box, 2, 0)
        form.addLayout(time_column, 2, 1)

        # 點擊次數
        self.count_label = self.label()

        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 999999999)
        self.count_spin.setValue(100)
        self.count_spin.setGroupSeparatorShown(True)
        self.count_spin.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons
        )

        self.infinite_check = QCheckBox()
        self.infinite_check.toggled.connect(self.count_spin.setDisabled)

        count_row = QHBoxLayout()
        count_row.setSpacing(14)
        count_row.addWidget(self.count_spin, 1)
        count_row.addWidget(self.infinite_check)

        form.addWidget(self.count_label, 3, 0)
        form.addLayout(count_row, 3, 1)

        root.addWidget(click_card)

        # ---------- 快捷鍵卡片 ----------
        hotkey_card, hotkey_layout, self.hotkey_title = self.make_card()

        self.start_hotkey_label = self.label()
        self.start_hotkey_combo = QComboBox()
        self.start_hotkey_combo.addItems(HOTKEY_DISPLAY)
        self.start_hotkey_combo.setMaxVisibleItems(12)
        self.start_hotkey_combo.setCurrentText("F2")

        self.stop_hotkey_label = self.label()
        self.stop_hotkey_combo = QComboBox()
        self.stop_hotkey_combo.addItems(HOTKEY_DISPLAY)
        self.stop_hotkey_combo.setMaxVisibleItems(12)
        self.stop_hotkey_combo.setCurrentText("F3")

        hotkey_row = QHBoxLayout()
        hotkey_row.setSpacing(12)
        hotkey_row.addWidget(self.start_hotkey_label)
        hotkey_row.addWidget(self.start_hotkey_combo, 1)
        hotkey_row.addSpacing(8)
        hotkey_row.addWidget(self.stop_hotkey_label)
        hotkey_row.addWidget(self.stop_hotkey_combo, 1)

        hotkey_layout.addLayout(hotkey_row)

        self.start_hotkey_combo.currentTextChanged.connect(
            self.on_hotkeys_changed
        )
        self.stop_hotkey_combo.currentTextChanged.connect(
            self.on_hotkeys_changed
        )

        root.addWidget(hotkey_card)

        # ---------- 狀態卡片 ----------
        status_card = QFrame()
        status_card.setObjectName("card")

        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(18, 14, 18, 14)
        status_layout.setSpacing(6)

        self.status_title = self.label()
        self.status_pill = self.label("statusPill")

        status_row = QHBoxLayout()
        status_row.setSpacing(12)
        status_row.addWidget(self.status_title)
        status_row.addWidget(self.status_pill)
        status_row.addStretch()

        self.status_detail_label = self.label("statusDetail")
        self.status_detail_label.setWordWrap(True)
        self.status_detail_label.hide()

        status_layout.addLayout(status_row)
        status_layout.addWidget(self.status_detail_label)

        root.addWidget(status_card)

        # ---------- 按鈕 ----------
        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self.start_button = QPushButton()
        self.start_button.setObjectName("startButton")

        self.stop_button = QPushButton()
        self.stop_button.setObjectName("stopButton")

        self.exit_button = QPushButton("EXIT")
        self.exit_button.setObjectName("exitButton")

        for button in (self.start_button, self.stop_button,
                       self.exit_button):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.start_button.clicked.connect(self.start_clicking)
        self.stop_button.clicked.connect(self.stop_clicking)

        # EXIT 直接關閉，不顯示確認視窗
        self.exit_button.clicked.connect(self.close)

        buttons.addWidget(self.start_button, 2)
        buttons.addWidget(self.stop_button, 2)
        buttons.addWidget(self.exit_button, 1)

        root.addLayout(buttons)

        # ---------- 底部提示 ----------
        self.hint_label = self.label("hint")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.hint_label)

        # 執行中要鎖定的設定欄位
        self.lockable_widgets = [
            self.mouse_combo,
            self.action_combo,
            self.hours_spin,
            self.minutes_spin,
            self.seconds_spin,
            self.tenth_spin,
            self.hundredth_spin,
            self.count_spin,
            self.infinite_check,
            self.start_hotkey_combo,
            self.stop_hotkey_combo,
            *self.step_buttons,
        ]

    # -----------------------------------------------------
    # 中英文介面
    # -----------------------------------------------------

    def change_language(self, language):
        self.current_language = language
        self.update_language()

    def update_language(self):
        self.subtitle_label.setText(self.t("subtitle"))
        self.language_label.setText(self.t("language"))

        self.click_title.setText(self.t("section_click"))
        self.mouse_label.setText(self.t("mouse"))
        self.mouse_combo.setItemText(0, self.t("left"))
        self.mouse_combo.setItemText(1, self.t("right"))

        self.action_label.setText(self.t("action"))
        self.action_combo.setItemText(0, self.t("single"))
        self.action_combo.setItemText(1, self.t("double"))

        self.interval_label.setText(self.t("interval"))
        self.hours_caption.setText(self.t("hours"))
        self.minutes_caption.setText(self.t("minutes"))
        self.seconds_caption.setText(self.t("seconds"))
        self.tenth_caption.setText(self.t("tenth"))
        self.hundredth_caption.setText(self.t("hundredth"))

        self.count_label.setText(self.t("count"))
        self.infinite_check.setText(self.t("infinite"))

        self.hotkey_title.setText(self.t("section_hotkey"))
        self.start_hotkey_label.setText(self.t("start_hotkey"))
        self.stop_hotkey_label.setText(self.t("stop_hotkey"))

        self.status_title.setText(self.t("status"))
        self.hint_label.setText(self.t("hint"))

        self.update_hotkey_button_text()
        self.update_interval_summary()
        self.set_status(self.status_state, self.status_detail)

    def update_hotkey_button_text(self):
        self.start_button.setText(
            f"START  ({self.start_hotkey_combo.currentText()})"
        )
        self.stop_button.setText(
            f"STOP  ({self.stop_hotkey_combo.currentText()})"
        )

    # -----------------------------------------------------
    # 狀態顯示
    # -----------------------------------------------------

    def set_status(self, state, detail=""):
        self.status_state = state
        self.status_detail = detail

        self.status_pill.setText("●  " + self.t(f"status_{state}"))

        # 依狀態套用不同顏色
        self.status_pill.setProperty("state", state)
        self.status_pill.style().unpolish(self.status_pill)
        self.status_pill.style().polish(self.status_pill)

        self.status_detail_label.setText(detail)
        self.status_detail_label.setVisible(bool(detail))

    def set_running_ui(self, running):
        for widget in self.lockable_widgets:
            widget.setEnabled(not running)

        if not running:
            self.count_spin.setEnabled(
                not self.infinite_check.isChecked()
            )

        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    # -----------------------------------------------------
    # 計算點擊間隔
    # -----------------------------------------------------

    def get_interval(self):
        return (
            self.hours_spin.value() * 3600
            + self.minutes_spin.value() * 60
            + self.seconds_spin.value()
            + self.tenth_spin.value() / 10
            + self.hundredth_spin.value() / 100
        )

    def update_interval_summary(self, *_):
        interval = self.get_interval()

        if interval == 0:
            self.interval_summary.setText(self.t("interval_zero"))
        else:
            self.interval_summary.setText(
                self.t("interval_summary").format(interval)
            )

    # -----------------------------------------------------
    # 防止兩個快捷鍵相同
    # -----------------------------------------------------

    def on_hotkeys_changed(self, *_):
        if self.closing:
            return

        start_key = self.start_hotkey_combo.currentText()
        stop_key = self.stop_hotkey_combo.currentText()

        if start_key == stop_key:
            sender = self.sender()

            if sender is self.start_hotkey_combo:
                self.start_hotkey_combo.blockSignals(True)
                self.start_hotkey_combo.setCurrentText(
                    self.last_start_hotkey
                )
                self.start_hotkey_combo.blockSignals(False)
            else:
                self.stop_hotkey_combo.blockSignals(True)
                self.stop_hotkey_combo.setCurrentText(
                    self.last_stop_hotkey
                )
                self.stop_hotkey_combo.blockSignals(False)

            return

        self.last_start_hotkey = start_key
        self.last_stop_hotkey = stop_key

        self.update_hotkey_button_text()
        self.restart_hotkey_listener()

    # -----------------------------------------------------
    # 全域快捷鍵監聽
    # -----------------------------------------------------

    def start_hotkey_listener(self):
        if self.closing:
            return

        start_key = DISPLAY_TO_HOTKEY[self.start_hotkey_combo.currentText()]
        stop_key = DISPLAY_TO_HOTKEY[self.stop_hotkey_combo.currentText()]

        if start_key == stop_key:
            return

        try:
            self.listener = keyboard.GlobalHotKeys({
                start_key: self.bridge.start_requested.emit,
                stop_key: self.bridge.stop_requested.emit,
            })
            self.listener.start()

            if self.status_state == "error":
                self.set_status("ready")

        except Exception as exc:
            self.listener = None
            self.set_status(
                "error", self.t("hotkey_error").format(exc)
            )

    def stop_hotkey_listener(self):
        listener = self.listener
        self.listener = None

        if listener is not None:
            try:
                listener.stop()

                if listener.is_alive():
                    listener.join(timeout=1.0)

            except Exception:
                pass

    def restart_hotkey_listener(self):
        self.stop_hotkey_listener()
        self.start_hotkey_listener()

    # -----------------------------------------------------
    # 開始點擊
    # -----------------------------------------------------

    def start_clicking(self):
        if self.closing:
            return

        if self.worker is not None and self.worker.isRunning():
            return

        click_count = (
            0 if self.infinite_check.isChecked()
            else self.count_spin.value()
        )

        self.set_status("running")
        self.set_running_ui(True)

        self.worker = ClickWorker(
            button=self.mouse_combo.currentData(),
            clicks=self.action_combo.currentData(),
            interval=self.get_interval(),
            click_count=click_count,
        )

        self.worker.error_occurred.connect(self.show_worker_error)
        self.worker.finished.connect(self.on_worker_finished)

        self.worker.start()

    # -----------------------------------------------------
    # 停止點擊
    # -----------------------------------------------------

    def stop_clicking(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.stop_button.setEnabled(False)
            self.set_status("stopping")

    def on_worker_finished(self):
        if self.closing:
            return

        self.set_running_ui(False)

        # 若是因錯誤停止，保留錯誤訊息
        if self.status_state != "error":
            self.set_status("ready")

    def show_worker_error(self, message):
        if not self.closing:
            self.set_status("error", message)

    # -----------------------------------------------------
    # EXIT：直接關閉，不詢問
    # -----------------------------------------------------

    def closeEvent(self, event):
        self.closing = True

        # 先停止全域快捷鍵
        self.stop_hotkey_listener()

        # 停止背景點擊執行緒
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        event.accept()


# =========================================================
# 程式入口
# =========================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft JhengHei UI", 10))

    window = AutoClicker()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()