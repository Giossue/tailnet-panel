"""Comprobaciones de tema, iconos, cursor y acciones dentro de tablas."""
import os
import unittest
from collections import Counter
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QEvent, QPointF, Qt
from PyQt6.QtGui import QEnterEvent, QFocusEvent, QIcon, QPalette
from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFileIconProvider, QMessageBox, QPushButton, QRadioButton, QScrollArea, QTabBar, QToolButton, QTreeView, QWidget

from app.config import config
from app.ui.components.controls import AppButton, InteractionFeedback, TableActionButton
from app.ui.icons import get_icon
from app.ui.theme import apply_theme, get_theme_colors
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.accounts_view import AccountsView
from app.ui.main_window import MainWindow
from app.ui.components.status_console import StatusConsole
from app.ui.components.command_dialog import CommandDialog
from app.core.command_registry import COMMANDS_BY_ID


def dominant_opaque_color(icon):
    image = icon.pixmap(24, 24).toImage()
    colors = Counter(
        image.pixelColor(x, y).name()
        for x in range(image.width()) for y in range(image.height())
        if image.pixelColor(x, y).alpha() > 200
    )
    return colors.most_common(1)[0][0]


def contrast_ratio(first, second):
    def luminance(value):
        rgb = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else
                  ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    low, high = sorted((luminance(first), luminance(second)))
    return (high + 0.05) / (low + 0.05)


class UiFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        if getattr(cls.app, "_interaction_feedback", None) is None:
            cls.app._interaction_feedback = InteractionFeedback(cls.app)

    def setUp(self):
        self.old_theme = config.theme

    def tearDown(self):
        config.theme = self.old_theme
        apply_theme(self.app, self.old_theme)

    def test_same_icon_changes_with_theme(self):
        config.theme = "dark"
        dark_icon = get_icon("settings")
        self.assertEqual(dominant_opaque_color(dark_icon), get_theme_colors("dark")["icon"])
        config.theme = "light"
        light_icon = get_icon("settings")
        self.assertEqual(dominant_opaque_color(light_icon), get_theme_colors("light")["icon"])

    def test_requested_palette_and_primary_button_contrast(self):
        for theme, background, card in (
            ("dark", "#171719", "#232229"),
            ("light", "#f4f6f9", "#fdfdfe"),
        ):
            colors = get_theme_colors(theme)
            self.assertEqual(colors["bg"].lower(), background)
            self.assertEqual(colors["panel"].lower(), card)
            self.assertEqual(colors["primary"], "#307BFC")
            self.assertGreaterEqual(contrast_ratio("#ffffff", colors["primary_button"]), 4.5)
            self.assertGreaterEqual(contrast_ratio("#ffffff", colors["primary_hover"]), 4.5)
            self.assertGreaterEqual(contrast_ratio("#ffffff", colors["primary_pressed"]), 4.5)

    def test_button_icon_follows_variant_hover_and_disabled_state(self):
        config.theme = "dark"
        button = AppButton("Acción")
        button.set_icon("settings")
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)
        self.assertEqual(dominant_opaque_color(button.icon()), get_theme_colors("dark")["icon"])

        self.app.sendEvent(button, QEnterEvent(QPointF(2, 2), QPointF(2, 2), QPointF(2, 2)))
        self.assertEqual(dominant_opaque_color(button.icon()), get_theme_colors("dark")["icon_hover"])
        self.app.sendEvent(button, QEvent(QEvent.Type.Leave))
        self.assertEqual(dominant_opaque_color(button.icon()), get_theme_colors("dark")["icon"])

        button.setProperty("class", "btn-primary")
        self.assertEqual(dominant_opaque_color(button.icon()), "#ffffff")
        button.setDown(True)
        button.refresh_icon()
        self.assertEqual(dominant_opaque_color(button.icon()), "#ffffff")
        button.setDown(False)
        button.refresh_icon()
        button.setProperty("class", "btn-danger")
        self.assertEqual(dominant_opaque_color(button.icon()), get_theme_colors("dark")["danger"])
        button.setDown(True)
        button.refresh_icon()
        self.assertEqual(dominant_opaque_color(button.icon()), "#ffffff")
        button.setDown(False)
        button.refresh_icon()
        button.setEnabled(False)
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.ArrowCursor)
        self.assertEqual(dominant_opaque_color(button.icon()), get_theme_colors("dark")["icon_disabled"])

    def test_focus_ring_is_only_for_keyboard_navigation(self):
        button = AppButton("Acción")
        self.app.sendEvent(button, QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.MouseFocusReason))
        self.assertEqual(button.property("keyboardFocus"), "false")
        self.app.sendEvent(button, QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.TabFocusReason))
        self.assertEqual(button.property("keyboardFocus"), "true")
        self.app.sendEvent(button, QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.TabFocusReason))
        self.assertEqual(button.property("keyboardFocus"), "false")

    def test_other_clickable_controls_use_hand_cursor(self):
        for widget in (QCheckBox("Filtro"), QRadioButton("Opción"), QComboBox(), QTabBar()):
            widget.show()
            self.app.processEvents()
            self.assertEqual(widget.cursor().shape(), Qt.CursorShape.PointingHandCursor)
            widget.setEnabled(False)
            self.assertEqual(widget.cursor().shape(), Qt.CursorShape.ArrowCursor)
            widget.close()

    def test_status_dot_uses_green_and_red_in_both_themes(self):
        from app.ui.theme import generate_qss
        for theme in ("dark", "light"):
            config.theme = theme
            self.app.setStyleSheet(generate_qss(theme))
            console = StatusConsole()
            console.show()
            for connected, expected in (
                (True, "status_connected"),
                (False, "status_disconnected"),
            ):
                console.set_status(connected, "equipo", "100.0.0.1")
                self.app.processEvents()
                color = console.status_dot.grab().toImage().pixelColor(6, 6).name()
                self.assertEqual(color, get_theme_colors(theme)[expected])
            console.close()

    def test_message_box_removes_native_button_icons(self):
        from app.ui.theme import generate_qss
        for theme in ("dark", "light"):
            config.theme = theme
            self.app.setStyleSheet(generate_qss(theme))
            box = QMessageBox(
                QMessageBox.Icon.Information, "Copiado", "Texto copiado",
                QMessageBox.StandardButton.Ok,
            )
            button = box.button(QMessageBox.StandardButton.Ok)
            button.setIcon(get_icon("check", color="#ffffff"))
            box.show()
            self.app.processEvents()
            self.assertTrue(button.icon().isNull())
            self.assertEqual(
                dominant_opaque_color(QIcon(box.iconPixmap())),
                get_theme_colors(theme)["accent"],
            )
            box.close()

    def test_file_dialog_uses_theme_palette_and_semantic_icons(self):
        for theme in ("dark", "light"):
            config.theme = theme
            apply_theme(self.app, theme)
            dialog = QFileDialog(None, "Seleccionar archivo")
            dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
            try:
                dialog.show()
                self.app.processEvents()
                colors = get_theme_colors(theme)
                tree = dialog.findChild(QTreeView)
                self.assertIsNotNone(tree)
                self.assertEqual(tree.palette().color(QPalette.ColorRole.Base).name(), colors["panel"].lower())
                folder_icon = dialog.iconProvider().icon(QFileIconProvider.IconType.Folder)
                self.assertEqual(dominant_opaque_color(folder_icon), colors["icon"])
                new_folder = dialog.findChild(QToolButton, "newFolderButton")
                self.assertEqual(dominant_opaque_color(new_folder.icon()), colors["icon"])
                for button in dialog.findChildren(QPushButton):
                    self.assertTrue(button.icon().isNull())
                    if button.isEnabled():
                        self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)
            finally:
                dialog.close()

    def test_peer_actions_fit_inside_each_row(self):
        view = DashboardView()
        view.apply_status({"Peer": {
            str(index): {"HostName": f"host-{index}", "TailscaleIPs": [f"100.0.0.{index}"],
                         "OS": "linux", "Online": True}
            for index in range(1, 4)
        }})
        view.resize(1000, 500)
        view.show()
        self.app.processEvents()
        table = view.peers_table
        self.assertEqual(table.rowCount(), 3)
        for row in range(3):
            host = table.cellWidget(row, 5)
            button = host.findChild(TableActionButton)
            self.assertEqual(table.rowHeight(row), 40)
            self.assertEqual(button.height(), 28)
            self.assertGreaterEqual(button.geometry().top(), 4)
            self.assertLessEqual(button.geometry().bottom(), host.rect().bottom() - 4)
        view.close()

    def test_theme_toggle_refreshes_tab_and_tray_icons(self):
        config.theme = "dark"
        window = MainWindow()
        try:
            dark_tab = dominant_opaque_color(window.main_tabs.tabIcon(0))
            dark_tray = dominant_opaque_color(window.tray_icon.contextMenu().actions()[0].icon())
            self.assertEqual(dark_tab, get_theme_colors("dark")["accent"])
            window.main_tabs.setCurrentIndex(2)
            self.assertEqual(dominant_opaque_color(window.main_tabs.tabIcon(2)), get_theme_colors("dark")["accent"])
            self.assertEqual(dominant_opaque_color(window.main_tabs.tabIcon(0)), get_theme_colors("dark")["icon"])
            window.toggle_theme()
            light_tab = dominant_opaque_color(window.main_tabs.tabIcon(2))
            light_tray = dominant_opaque_color(window.tray_icon.contextMenu().actions()[0].icon())
            self.assertEqual(light_tab, get_theme_colors("light")["accent"])
            self.assertEqual(dominant_opaque_color(window.main_tabs.tabIcon(0)), get_theme_colors("light")["icon"])
            self.assertNotEqual(dark_tab, light_tab)
            self.assertNotEqual(dark_tray, light_tray)
        finally:
            window.close()

    def test_small_window_scrolls_forms_without_horizontal_overflow(self):
        window = MainWindow()
        try:
            window.resize(920, 640)
            window.show()
            for view_index, tabs in ((2, window.services_tab), (8, window.config_tab), (6, window.services_tab)):
                window.switch_view(view_index)
                self.app.processEvents()
                scroll = tabs.currentWidget()
                self.assertIsInstance(scroll, QScrollArea)
                self.assertGreater(scroll.verticalScrollBar().maximum(), 0)
                self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        finally:
            window.close()

    def test_long_command_dialog_fits_small_window_with_preview_visible(self):
        parent = QWidget()
        parent.resize(920, 640)
        parent.show()
        dialog = CommandDialog(COMMANDS_BY_ID[1], parent)
        try:
            dialog.show()
            self.app.processEvents()
            scroll = dialog.content_scroll
            self.assertLessEqual(dialog.height(), 600)
            self.assertGreater(scroll.verticalScrollBar().maximum(), 0)
            self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
            self.assertTrue(dialog.preview_group.isVisible())
            self.assertTrue(dialog.btn_run.isVisible())
            self.assertLess(dialog.preview_group.geometry().bottom(), dialog.btn_run.geometry().top())
        finally:
            dialog.close()
            parent.close()

        file_dialog = CommandDialog(COMMANDS_BY_ID[4])
        try:
            self.assertNotIsInstance(file_dialog.param_widgets["cert_file"][1], QDialog)
        finally:
            file_dialog.close()

    def test_account_list_uses_profile_ids_and_marks_current_profile(self):
        with patch("app.ui.views.accounts_view.AsyncTailscaleQuery.run"):
            view = AccountsView()
            try:
                view._on_accounts_response('''[
                  {"id":"1672","account":"actual@example.com","tailnet":"equipo","selected":true},
                  {"id":"2f87","account":"otra@example.com","tailnet":"equipo","selected":false}
                ]''')
                self.assertEqual(view.accounts_list_widget.count(), 2)
                self.assertIn("Actual", view.accounts_list_widget.item(0).text())
                view.accounts_list_widget.setCurrentRow(1)
                self.assertEqual(view.account_target_input.text(), "2f87")
            finally:
                view.close()


if __name__ == "__main__":
    unittest.main()
