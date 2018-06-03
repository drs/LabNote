"""
This module contain the classes responsible for launching and managing the LabNote MainWindow.
"""


from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QFile, QTextStream

from ui.ui_mainwindow import Ui_MainWindow
from common import style
import resources.resources


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class responsible of launching the LabNote MainWindow interface
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Set style sheet
        style.set_style_sheet(self, ":/StyleSheet/style-sheet/main_window.qss")

        # Remove focus rectangle
        self.lst_notebook.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.lst_entry.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Set no entry widget as default widget
        self.set_no_entry_widget()

    def set_no_entry_widget(self):
        """
        Method that show the no entry selected widget
        :return: None
        """
        # Setting up widget elements
        no_entry_pixmap = QPixmap(":/MainWindow/Icons/icons/main-window/no_entry_selected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        lbl_no_entry_image.show()

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)
        style.set_style_sheet(lbl_no_entry, ":/StyleSheet/style-sheet/main-window/no_entry_label.qss")

        # Setting up the layout
        self.no_entry_widget = QWidget()
        main_layout = QVBoxLayout(self.no_entry_widget)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)

        # Add widget to mainwindow
        self.centralWidget().layout().addWidget(self.no_entry_widget, Qt.AlignHCenter, Qt.AlignCenter)
