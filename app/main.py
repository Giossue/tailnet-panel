"""
Punto de entrada principal de Tailnet Panel.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.config import APP_NAME, APP_ORG
from app.ui.main_window import MainWindow

def main():
    # Permitir renderizado nítido en pantallas HiDPI
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setDesktopFileName(APP_NAME.lower().replace(" ", "-"))
    app.setOrganizationName(APP_ORG)
    app.setQuitOnLastWindowClosed(True)

    from app.ui.icons import get_app_icon
    app.setWindowIcon(get_app_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
