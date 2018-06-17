"""Script de lancement du programme GUIDE-CFR"""

# Python import
import sys

# PyQt import
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Project import
from labnote.interface.main_window import MainWindow
from labnote.core import stylesheet

# Permettre les écrans High DPI avec PyQt5
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application icon
    app.setWindowIcon(QIcon(":/Icons/App/icons/main/appicon.png"))

    # Set application stylesheet
    stylesheet.set_style_sheet(app, ":/StyleSheet/style-sheet/application.qss")

    # Afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
