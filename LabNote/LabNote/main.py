"""Script de lancement du programme GUIDE-CFR"""

# Python import
import sys

# PyQt import
from PyQt5.QtWidgets import QApplication

# Project import
from mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
