"""Controles reutilizables con feedback consistente en todas las vistas."""
from PyQt6.QtCore import QEvent, QFileInfo, QObject, QPoint, QPointF, QRect, Qt, QSize
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPen
from PyQt6.QtWidgets import (
    QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QHBoxLayout, QLayout,
    QFileDialog, QFileIconProvider, QMenu, QMessageBox, QPushButton,
    QRadioButton, QSizePolicy, QSpinBox, QStyle, QToolButton,
    QStyleOptionButton, QStyleOptionComboBox, QStyleOptionSpinBox, QTabBar,
    QTabWidget, QTableWidget, QWidget,
)

from app.config import config
from app.ui.icons import get_icon, icon_color
from app.ui.theme import get_theme_colors


class AppButton(QPushButton):
    """Botón semántico: cursor, foco e icono siguen su estado y variante."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._icon_name = None
        self._hovered = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setIconSize(QSize(14, 14))
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.pressed.connect(self.refresh_icon)
        self.released.connect(self.refresh_icon)

    def set_icon(self, name: str):
        self._icon_name = name
        self.refresh_icon()

    def setProperty(self, name, value):
        result = super().setProperty(name, value)
        if name in ("class", "state"):
            self.refresh_icon()
        return result

    def _icon_role(self):
        classes = str(self.property("class") or "")
        if "btn-danger" in classes:
            return "danger"
        if "btn-primary" in classes:
            return "primary"
        if self.objectName() == "StatusAction" and self.property("state") == "disconnected":
            return "primary"
        return "default"

    def refresh_icon(self):
        if not getattr(self, "_icon_name", None):
            return
        state = (
            "disabled" if not self.isEnabled() else
            "pressed" if self.isDown() else
            "active" if self._hovered else "normal"
        )
        color = icon_color(self._icon_role(), state)
        super().setIcon(get_icon(self._icon_name, color=color))

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovered = True
        self.refresh_icon()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered = False
        self.refresh_icon()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if self.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )
            self.refresh_icon()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._set_keyboard_focus(event.reason() in (
            Qt.FocusReason.TabFocusReason,
            Qt.FocusReason.BacktabFocusReason,
            Qt.FocusReason.ShortcutFocusReason,
        ))

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._set_keyboard_focus(False)

    def _set_keyboard_focus(self, visible: bool):
        self.setProperty("keyboardFocus", "true" if visible else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class AppCheckBox(QCheckBox):
    """Casilla con marca visible sobre el color primario en ambos temas."""

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.checkState() != Qt.CheckState.Checked:
            return
        option = QStyleOptionButton()
        option.initFrom(self)
        indicator = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, self)
        if not indicator.isValid():
            return
        color = "#ffffff" if self.isEnabled() else icon_color("default", "disabled")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        center = indicator.center()
        x, y = center.x(), center.y()
        painter.drawLine(QPointF(x - 4, y), QPointF(x - 1, y + 3))
        painter.drawLine(QPointF(x - 1, y + 3), QPointF(x + 4.5, y - 3))
        painter.end()


class AppRadioButton(QRadioButton):
    """Botón de opción con punto primario y tamaño constante al marcarse."""

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isChecked():
            return
        option = QStyleOptionButton()
        option.initFrom(self)
        indicator = self.style().subElementRect(QStyle.SubElement.SE_RadioButtonIndicator, option, self)
        if not indicator.isValid():
            return
        color = get_theme_colors(config.theme)["primary"] if self.isEnabled() else icon_color("default", "disabled")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawEllipse(QPointF(indicator.center()), 4.0, 4.0)
        painter.end()


class AppSpinBox(QSpinBox):
    """Selector numérico con flechas visibles en los dos temas."""

    def paintEvent(self, event):
        super().paintEvent(event)
        option = QStyleOptionSpinBox()
        option.initFrom(self)
        option.frame = self.hasFrame()
        option.buttonSymbols = self.buttonSymbols()
        option.stepEnabled = self.stepEnabled()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for control, direction, enabled_flag in (
            (QStyle.SubControl.SC_SpinBoxUp, 1, QAbstractSpinBox.StepEnabledFlag.StepUpEnabled),
            (QStyle.SubControl.SC_SpinBoxDown, -1, QAbstractSpinBox.StepEnabledFlag.StepDownEnabled),
        ):
            rect = self.style().subControlRect(QStyle.ComplexControl.CC_SpinBox, option, control, self)
            if not rect.isValid():
                continue
            arrow_enabled = self.isEnabled() and bool(option.stepEnabled & enabled_flag)
            color = icon_color("default", "normal" if arrow_enabled else "disabled")
            pen = QPen(QColor(color), 1.7)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            center = rect.center()
            x, y = center.x(), center.y()
            painter.drawLine(QPointF(x - 3, y + direction), QPointF(x, y - direction * 2))
            painter.drawLine(QPointF(x, y - direction * 2), QPointF(x + 3, y + direction))
        painter.end()


class AppComboBox(QComboBox):
    """Lista desplegable con flecha visible y colores del tema."""

    def paintEvent(self, event):
        super().paintEvent(event)
        option = QStyleOptionComboBox()
        option.initFrom(self)
        option.editable = self.isEditable()
        option.currentText = self.currentText()
        arrow = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox, option,
            QStyle.SubControl.SC_ComboBoxArrow, self,
        )
        if not arrow.isValid():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        state = "disabled" if not self.isEnabled() else "active" if self.underMouse() else "normal"
        pen = QPen(QColor(icon_color("default", state)), 1.7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        center = arrow.center()
        x, y = center.x(), center.y()
        painter.drawLine(QPointF(x - 3.5, y - 1.5), QPointF(x, y + 2))
        painter.drawLine(QPointF(x, y + 2), QPointF(x + 3.5, y - 1.5))
        painter.end()


class TableActionButton(AppButton):
    """Botón compacto que no se estira hasta los bordes de una celda."""

    def __init__(self, text="", icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", "btn-table")
        self.setFixedHeight(28)
        self.setIconSize(QSize(14, 14))
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        if icon_name:
            self.set_icon(icon_name)


def table_action_cell(*buttons: AppButton) -> QWidget:
    """Contenedor transparente que deja aire alrededor de las acciones."""
    host = QWidget()
    host.setObjectName("TableActionCell")
    host.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    layout = QHBoxLayout(host)
    layout.setContentsMargins(6, 4, 6, 4)
    layout.setSpacing(5)
    layout.addStretch()
    for button in buttons:
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignVCenter)
    return host


def configure_action_table(table: QTableWidget):
    table.verticalHeader().setDefaultSectionSize(40)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)


class FlowLayout(QLayout):
    """Distribuye botones en más de una fila cuando falta ancho."""

    def __init__(self, parent=None, h_spacing=8, v_spacing=8):
        super().__init__(parent)
        self._items = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        left, top, right, bottom = self.getContentsMargins()
        return self._layout_items(QRect(0, 0, max(0, width - left - right), 0), True) + top + bottom

    def setGeometry(self, rect):
        super().setGeometry(rect)
        left, top, right, bottom = self.getContentsMargins()
        area = rect.adjusted(left, top, -right, -bottom)
        self._layout_items(area, False)

    def sizeHint(self):
        left, top, right, bottom = self.getContentsMargins()
        widths = [item.sizeHint().width() for item in self._items]
        heights = [item.sizeHint().height() for item in self._items]
        return QSize(sum(widths) + max(0, len(widths) - 1) * self._h_spacing + left + right,
                     max(heights, default=0) + top + bottom)

    def minimumSize(self):
        left, top, right, bottom = self.getContentsMargins()
        widths = [item.minimumSize().width() for item in self._items]
        heights = [item.minimumSize().height() for item in self._items]
        return QSize(max(widths, default=0) + left + right,
                     max(heights, default=0) + top + bottom)

    def _layout_items(self, rect, measure_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        for item in self._items:
            size = item.sizeHint()
            if x > rect.x() and x + size.width() > rect.x() + rect.width():
                x = rect.x()
                y += line_height + self._v_spacing
                line_height = 0
            if not measure_only:
                item.setGeometry(QRect(QPoint(x, y), size))
            x += size.width() + self._h_spacing
            line_height = max(line_height, size.height())
        return y + line_height - rect.y()


class InteractionFeedback(QObject):
    """Cursores coherentes para controles Qt que no usan AppButton."""

    def __init__(self, app: QApplication):
        super().__init__(app)
        self.app = app
        app.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Show and isinstance(watched, QMessageBox):
            self._style_message_box(watched)
        if event.type() == QEvent.Type.Show and isinstance(watched, QFileDialog):
            self._style_file_dialog(watched)
        if event.type() == QEvent.Type.Show and isinstance(watched, QPushButton):
            parent = watched.parent()
            while parent is not None:
                if isinstance(parent, (QMessageBox, QFileDialog)):
                    watched.setIcon(QIcon())
                    watched.setCursor(
                        Qt.CursorShape.PointingHandCursor if watched.isEnabled()
                        else Qt.CursorShape.ArrowCursor
                    )
                    break
                parent = parent.parent()
        if event.type() in (QEvent.Type.Polish, QEvent.Type.EnabledChange):
            if isinstance(watched, (QCheckBox, QRadioButton, QComboBox, QTabBar,
                                    QToolButton, QPushButton)):
                watched.setCursor(
                    Qt.CursorShape.PointingHandCursor if watched.isEnabled()
                    else Qt.CursorShape.ArrowCursor
                )
        return False

    def _style_file_dialog(self, dialog: QFileDialog):
        dialog._theme_icon_provider = ThemeFileIconProvider()
        dialog.setIconProvider(dialog._theme_icon_provider)
        self._refresh_file_location_icon(dialog)
        dialog.directoryEntered.connect(lambda _: self._refresh_file_location_icon(dialog))
        button_icons = {
            "backButton": "chevron-left",
            "forwardButton": "chevron-right",
            "toParentButton": "arrow-up",
            "newFolderButton": "folder-plus",
            "listModeButton": "list",
            "detailModeButton": "list-detail",
        }
        for button in dialog.findChildren(QToolButton):
            name = button_icons.get(button.objectName())
            if name:
                button.setIcon(get_icon(name))
        for button in dialog.findChildren(QPushButton):
            button.setIcon(QIcon())
            button.setCursor(
                Qt.CursorShape.PointingHandCursor if button.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )

    def _refresh_file_location_icon(self, dialog: QFileDialog):
        location = dialog.findChild(QComboBox, "lookInCombo")
        if location is not None:
            for index in range(location.count()):
                location.setItemIcon(index, get_icon("folder"))

    def _style_message_box(self, box: QMessageBox):
        semantic = box.property("semanticMessageIcon")
        if not semantic:
            semantic = {
                QMessageBox.Icon.Information: ("info", "accent"),
                QMessageBox.Icon.Warning: ("warning", "danger"),
                QMessageBox.Icon.Critical: ("times", "danger"),
                QMessageBox.Icon.Question: ("info", "accent"),
            }.get(box.icon())
            if semantic:
                box.setProperty("semanticMessageIcon", semantic)
        if semantic:
            name, role = semantic
            box.setIconPixmap(get_icon(name, role=role).pixmap(36, 36))
        for button in box.findChildren(QPushButton):
            button.setIcon(QIcon())
            button.setCursor(
                Qt.CursorShape.PointingHandCursor if button.isEnabled()
                else Qt.CursorShape.ArrowCursor
            )


class ThemeFileIconProvider(QFileIconProvider):
    """Iconos de archivos y carpetas que conservan contraste en ambos temas."""

    def icon(self, item):
        if isinstance(item, QFileInfo):
            return get_icon("folder" if item.isDir() else "file")
        names = {
            QFileIconProvider.IconType.Computer: "device",
            QFileIconProvider.IconType.Desktop: "device",
            QFileIconProvider.IconType.Drive: "folder",
            QFileIconProvider.IconType.File: "file",
            QFileIconProvider.IconType.Folder: "folder",
            QFileIconProvider.IconType.Network: "web",
            QFileIconProvider.IconType.Trashcan: "trash",
        }
        name = names.get(item)
        return get_icon(name) if name else super().icon(item)


def refresh_button_icons(root: QWidget):
    for button in root.findChildren(AppButton):
        button.refresh_icon()


def set_tab_icon(tabs: QTabWidget, index: int, name: str):
    tabs.tabBar().setTabData(index, name)
    if not tabs.property("semanticTabsConnected"):
        tabs.currentChanged.connect(lambda _: _refresh_one_tab_widget(tabs))
        tabs.setProperty("semanticTabsConnected", True)
    _refresh_one_tab_widget(tabs)


def _refresh_one_tab_widget(tabs: QTabWidget):
    for index in range(tabs.count()):
        name = tabs.tabBar().tabData(index)
        if isinstance(name, str) and name:
            role = "accent" if index == tabs.currentIndex() else "default"
            tabs.setTabIcon(index, get_icon(name, role=role))


def refresh_tab_icons(root: QWidget):
    for tabs in root.findChildren(QTabWidget):
        _refresh_one_tab_widget(tabs)


def set_action_icon(action: QAction, name: str):
    action.setProperty("iconName", name)
    action.setIcon(get_icon(name))


def refresh_action_icons(menu: QMenu):
    for action in menu.actions():
        name = action.property("iconName")
        if isinstance(name, str) and name:
            action.setIcon(get_icon(name))
