"""Paleta y estilos compartidos de la interfaz."""

from typing import Dict
from PyQt6.QtGui import QColor, QPalette

PALETTES = {
    "dark": {
        "bg": "#171719", "panel": "#232229", "surface": "#2d2c34",
        "input": "#1e1d23", "text": "#f4f4f7", "muted": "#b0afbb",
        "border": "#42414b", "hover": "#383844", "accent": "#8db7ff",
        "primary": "#307BFC", "accent_soft": "#2a3550",
        "success": "#8db7ff", "danger": "#f19aa6",
        "danger_soft": "#412831", "terminal": "#1c1b21",
        "table_alt": "#292830", "selection": "#303f60",
        "icon": "#c4c2ce", "icon_hover": "#f7f7fc", "icon_disabled": "#81818e",
        "primary_button": "#2565d5", "primary_hover": "#2b70ea",
        "primary_pressed": "#1b52ad", "danger_hover": "#b53d55",
        "danger_pressed": "#8e2d45", "danger_border": "#8f5865",
        "status_connected": "#53c695", "status_disconnected": "#e06b78",
        "warning": "#8db7ff", "focus": "#abcbff",
    },
    "light": {
        "bg": "#F4F6F9", "panel": "#FDFDFE", "surface": "#eceff4",
        "input": "#ffffff", "text": "#20232a", "muted": "#5c6674",
        "border": "#d9dfe8", "hover": "#e7edf7", "accent": "#225cbc",
        "primary": "#307BFC", "accent_soft": "#dfeaff",
        "success": "#225cbc", "danger": "#b72c45",
        "danger_soft": "#fcecef", "terminal": "#f5f7fb",
        "table_alt": "#f8f9fc", "selection": "#dee9fc",
        "icon": "#5e6878", "icon_hover": "#225cbc", "icon_disabled": "#9aa4b3",
        "primary_button": "#2565d5", "primary_hover": "#2b70ea",
        "primary_pressed": "#1b52ad", "danger_hover": "#b72c45",
        "danger_pressed": "#91213a", "danger_border": "#d68f9c",
        "status_connected": "#16805b", "status_disconnected": "#b83249",
        "warning": "#225cbc", "focus": "#225cbc",
    },
}

def get_theme_colors(theme: str = "dark") -> Dict[str, str]:
    return PALETTES.get(theme, PALETTES["dark"])


def generate_palette(theme: str = "dark") -> QPalette:
    """Da los mismos colores a controles Qt que no aceptan todos los selectores QSS."""
    c = get_theme_colors(theme)
    palette = QPalette()
    roles = {
        QPalette.ColorRole.Window: "bg",
        QPalette.ColorRole.WindowText: "text",
        QPalette.ColorRole.Base: "panel",
        QPalette.ColorRole.AlternateBase: "table_alt",
        QPalette.ColorRole.Text: "text",
        QPalette.ColorRole.Button: "surface",
        QPalette.ColorRole.ButtonText: "text",
        QPalette.ColorRole.Highlight: "selection",
        QPalette.ColorRole.HighlightedText: "text",
        QPalette.ColorRole.Link: "accent",
        QPalette.ColorRole.ToolTipBase: "panel",
        QPalette.ColorRole.ToolTipText: "text",
        QPalette.ColorRole.PlaceholderText: "muted",
    }
    for role, color_name in roles.items():
        palette.setColor(role, QColor(c[color_name]))
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text,
                 QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(c["muted"]))
    return palette


def apply_theme(app, theme: str = "dark") -> None:
    app.setPalette(generate_palette(theme))
    app.setStyleSheet(generate_qss(theme))

def generate_qss(theme: str = "dark") -> str:
    c = get_theme_colors(theme)
    return f"""
    QMainWindow, QWidget#CentralWidget {{ background: {c['bg']}; }}
    QWidget {{
        color: {c['text']};
        font-family: 'Inter', 'Noto Sans', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}
    QLabel {{ background: transparent; }}
    QLabel:disabled {{ color: {c['muted']}; }}
    QLabel[class="muted-copy"] {{ color: {c['muted']}; }}

    #AppHeader {{ background: transparent; }}
    #BrandMark {{
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}
    #BrandTitle {{ font-size: 17px; font-weight: 700; }}
    #BrandSubtitle {{ color: {c['muted']}; font-size: 12px; }}

    #StatusConsole {{
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QLabel#StatusDot {{
        background: {c['status_disconnected']};
        border-radius: 6px;
    }}
    QLabel#StatusDot[state="connected"] {{ background: {c['status_connected']}; }}
    QLabel#StatusDot[state="disconnected"] {{ background: {c['status_disconnected']}; }}
    #StatusEyebrow {{
        color: {c['muted']};
        font-size: 10px;
        font-weight: 700;
    }}
    #StatusHostLabel {{ font-size: 20px; font-weight: 700; }}
    QLabel[class="meta-badge"] {{ color: {c['muted']}; font-size: 12px; }}
    QLabel[class="kbd-pill"] {{
        color: {c['text']};
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 5px;
        padding: 3px 8px;
        font-family: 'DejaVu Sans Mono', monospace;
        font-size: 11px;
    }}

    QTabWidget {{ background: transparent; }}
    QTabWidget::pane {{
        background: {c['panel']};
        border: none;
    }}
    QTabWidget#MainTabs::pane {{ background: transparent; }}
    QTabWidget::tab-bar {{ left: 8px; }}
    QTabBar {{ background: transparent; }}
    QTabBar::tab {{
        background: transparent;
        color: {c['muted']};
        border: none;
        border-radius: 7px;
        padding: 8px 13px;
        margin-right: 4px;
        margin-bottom: 4px;
        font-weight: 600;
    }}
    QTabBar::tab:hover {{ color: {c['text']}; background: {c['hover']}; }}
    QTabBar::tab:selected {{
        color: {c['accent']};
        background: {c['accent_soft']};
    }}
    QTabBar::tab:selected:hover {{ background: {c['accent_soft']}; }}
    QScrollArea#ViewScrollArea, QScrollArea#ViewScrollArea > QWidget > QWidget {{
        background: {c['panel']}; border: none;
    }}
    QWidget#MainPage {{
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 9px;
    }}

    QFrame[class="card"], QFrame[class="node-card"] {{
        background: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 9px;
    }}
    QFrame#OperatorNotice {{
        background: {c['accent_soft']};
        border: 1px solid {c['border']};
        border-radius: 8px;
    }}
    QLabel[class="card-title"], QLabel[class="card-subtitle"] {{
        color: {c['muted']};
        font-size: 12px;
    }}
    QLabel[class="metric-value"] {{ font-size: 19px; font-weight: 700; }}
    QLabel#FunnelWarning {{
        background: {c['danger_soft']};
        color: {c['danger']};
        border: 1px solid {c['danger']};
        border-radius: 6px;
        padding: 10px;
    }}
    QLabel#CommandTitle {{ font-size: 15px; font-weight: 700; }}
    QLabel#CommandPreview {{
        background: {c['terminal']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 9px;
        font-family: 'DejaVu Sans Mono', monospace;
    }}

    QGroupBox {{
        background: {c['panel']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        margin-top: 17px;
        padding: 13px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 11px;
        padding: 0 5px;
        background: {c['panel']};
    }}

    QPushButton {{
        background: {c['surface']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 11px;
        min-height: 21px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: {c['hover']}; border-color: {c['accent']}; }}
    QPushButton:pressed {{ background: {c['accent_soft']}; border-color: {c['primary']}; }}
    QPushButton:disabled {{
        background: {c['surface']};
        color: {c['muted']};
        border-color: {c['border']};
    }}
    QPushButton[class="btn-primary"],
    QPushButton#StatusAction[state="disconnected"] {{
        background: {c['primary_button']};
        color: #ffffff;
        border-color: {c['primary_button']};
    }}
    QPushButton[class="btn-primary"]:hover,
    QPushButton#StatusAction[state="disconnected"]:hover {{
        background: {c['primary_hover']};
        border-color: {c['primary_hover']};
        color: #ffffff;
    }}
    QPushButton[class="btn-primary"]:pressed,
    QPushButton#StatusAction[state="disconnected"]:pressed {{
        background: {c['primary_pressed']}; border-color: {c['primary_pressed']}; color: #ffffff;
    }}
    QPushButton[class="btn-primary"]:disabled {{
        background: {c['surface']}; color: {c['muted']}; border-color: {c['border']};
    }}
    QPushButton[class="btn-danger"] {{
        background: {c['danger_soft']};
        color: {c['danger']};
        border-color: {c['danger_border']};
    }}
    QPushButton[class="btn-danger"]:hover {{
        background: {c['danger_hover']}; color: #ffffff; border-color: {c['danger_hover']};
    }}
    QPushButton[class="btn-danger"]:pressed {{
        background: {c['danger_pressed']}; color: #ffffff; border-color: {c['danger_pressed']};
    }}
    QPushButton[class="btn-danger"]:disabled {{
        background: {c['surface']};
        color: {c['muted']};
        border-color: {c['border']};
    }}
    QPushButton[class="btn-table"] {{ padding: 3px 8px; min-height: 20px; }}
    QPushButton[class="btn-table"]:hover {{ background: {c['accent_soft']}; border-color: {c['accent']}; }}
    QPushButton[class="btn-flat"] {{ background: transparent; border-color: transparent; }}
    QPushButton[class="btn-flat"]:hover {{ background: {c['hover']}; border-color: {c['border']}; }}
    QPushButton[keyboardFocus="true"] {{ border: 2px solid {c['focus']}; }}

    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
        background: {c['input']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 9px;
        selection-background-color: {c['selection']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
    QSpinBox:focus, QComboBox:focus {{ border-color: {c['accent']}; }}
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover,
    QSpinBox:hover, QComboBox:hover {{ border-color: {c['accent']}; }}
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 18px;
        background: {c['surface']};
        border-left: 1px solid {c['border']};
    }}
    QSpinBox::up-button {{ border-bottom: 1px solid {c['border']}; border-top-right-radius: 5px; }}
    QSpinBox::down-button {{ border-bottom-right-radius: 5px; }}
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {c['hover']}; }}
    QSpinBox::up-arrow, QSpinBox::down-arrow {{ image: none; width: 0px; height: 0px; }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox::drop-down:hover {{ background: {c['hover']}; }}
    QComboBox::down-arrow {{ image: none; width: 0px; height: 0px; }}
    QComboBox QAbstractItemView {{
        background: {c['panel']};
        color: {c['text']};
        border: 1px solid {c['border']};
        selection-background-color: {c['selection']};
    }}

    QTableWidget, QTreeWidget, QListWidget {{
        background: {c['panel']};
        alternate-background-color: {c['table_alt']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 7px;
        gridline-color: {c['border']};
        selection-background-color: {c['selection']};
        selection-color: {c['text']};
    }}
    QTableWidget::item:hover, QTreeWidget::item:hover, QListWidget::item:hover {{
        background: {c['hover']};
    }}
    QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {{
        background: {c['selection']}; color: {c['text']};
    }}
    QWidget#TableActionCell {{ background: transparent; border: none; }}
    QHeaderView::section {{
        background: {c['surface']};
        color: {c['muted']};
        border: none;
        border-bottom: 1px solid {c['border']};
        padding: 8px 10px;
        font-weight: 600;
    }}

    #TerminalPanel {{
        background: {c['terminal']};
        border: 1px solid {c['border']};
        border-radius: 8px;
    }}
    #TerminalHeader {{ background: {c['surface']}; border-radius: 7px; }}
    #TerminalStatus {{ color: {c['muted']}; font-size: 11px; }}
    #TerminalStatus[state="running"] {{ color: {c['accent']}; }}
    #TerminalStatus[state="success"] {{ color: {c['success']}; }}
    #TerminalStatus[state="error"] {{ color: {c['danger']}; }}
    #TerminalOutput {{
        background: {c['terminal']};
        border: none;
        border-radius: 0;
        font-family: 'DejaVu Sans Mono', monospace;
        font-size: 11px;
        padding: 10px;
    }}

    QScrollBar:vertical {{ background: transparent; width: 8px; }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        min-height: 22px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['muted']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 8px; }}
    QScrollBar::handle:horizontal {{ background: {c['border']}; border-radius: 4px; }}
    QScrollBar::handle:horizontal:hover {{ background: {c['muted']}; }}
    QCheckBox {{ spacing: 7px; }}
    QCheckBox:hover {{ color: {c['accent']}; }}
    QCheckBox::indicator {{
        width: 15px;
        height: 15px;
        border: 1px solid {c['border']};
        border-radius: 4px;
        background: {c['input']};
    }}
    QCheckBox::indicator:checked {{
        background: {c['primary']};
        border-color: {c['primary']};
    }}
    QCheckBox::indicator:hover {{ border-color: {c['accent']}; }}
    QCheckBox::indicator:disabled {{ background: {c['surface']}; border-color: {c['border']}; }}
    QRadioButton {{ spacing: 7px; }}
    QRadioButton:hover {{ color: {c['accent']}; }}
    QRadioButton::indicator {{
        width: 15px;
        height: 15px;
        border: 1px solid {c['border']};
        border-radius: 8px;
        background: {c['input']};
    }}
    QRadioButton::indicator:checked {{
        border-color: {c['primary']};
    }}
    QRadioButton::indicator:unchecked:hover {{ border-color: {c['accent']}; }}
    QRadioButton::indicator:disabled {{ border-color: {c['border']}; background: {c['surface']}; }}
    QDialog {{ background: {c['bg']}; }}
    QFileDialog QTreeView, QFileDialog QListView {{
        background: {c['panel']};
        alternate-background-color: {c['table_alt']};
        color: {c['text']};
        border: none;
        selection-background-color: {c['selection']};
        selection-color: {c['text']};
    }}
    QFileDialog QToolButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 4px;
    }}
    QFileDialog QToolButton:hover {{ background: {c['hover']}; border-color: {c['border']}; }}
    QFileDialog QToolButton:checked {{ background: {c['accent_soft']}; border-color: {c['accent']}; }}
    QFileDialog QToolButton:pressed {{ background: {c['accent_soft']}; border-color: {c['accent']}; }}
    QScrollArea#CommandDialogScroll, QWidget#CommandDialogContent {{
        background: {c['bg']}; border: none;
    }}
    QScrollArea#CommandDialogScroll QScrollBar:vertical,
    QScrollArea#CommandDialogScroll QScrollBar::add-page:vertical,
    QScrollArea#CommandDialogScroll QScrollBar::sub-page:vertical {{
        background: {c['bg']};
    }}
    QMessageBox {{ background: {c['panel']}; }}
    QMessageBox QPushButton {{ min-width: 84px; }}
    QMenu {{ background: {c['panel']}; color: {c['text']}; border: 1px solid {c['border']}; padding: 4px; }}
    QMenu::item {{ padding: 7px 18px 7px 28px; border-radius: 4px; }}
    QMenu::item:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}
    QMenu::item:disabled {{ color: {c['muted']}; }}
    QToolTip {{
        background: {c['panel']};
        color: {c['text']};
        border: 1px solid {c['border']};
    }}
    """

DARK_THEME_QSS = generate_qss("dark")
LIGHT_THEME_QSS = generate_qss("light")
