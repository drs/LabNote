"""Script de lancement du programme GUIDE-CFR"""

# Python import
import sys

# PyQt import
from PyQt5.QtWidgets import QApplication

# Project import
from interface.main_window import MainWindow
from common import style

if __name__ == "__main__":
    app = QApplication(sys.argv)

    style.set_style_sheet(app, ":/StyleSheet/style-sheet/application.qss")

    #app.setStyleSheet("QLabel { font: Bold 20pt Arial }")
    # Afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
