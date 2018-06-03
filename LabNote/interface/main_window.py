from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QFile, QTextStream

from ui.ui_mainwindow import Ui_MainWindow
import resources.resources


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Set style sheet
        self.set_style_sheet()

        # Set no entry widget as default widget
        self.set_no_entry_widget()

    def set_style_sheet(self):
        # Set style sheet
        qss = QFile(":/StyleSheet/Resources/StyleSheet/MainWindow.qss")
        qss.open(QFile.ReadOnly)
        style = QTextStream(qss).readAll()
        self.setStyleSheet(style)
        qss.close()

    def set_no_entry_widget(self):
        # Setting up widget elements
        no_entry_pixmap = QPixmap(":/MainWindow/Icons/Resources/Icons/MainWindow/NoEntrySelected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        lbl_no_entry_image.show()

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)

        # Setting up the layout
        self.no_entry_widget = QWidget()
        main_layout = QVBoxLayout(self.no_entry_widget)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)

        # Add widget to mainwindow
        self.centralWidget().layout().addWidget(self.no_entry_widget, Qt.AlignHCenter, Qt.AlignCenter)
