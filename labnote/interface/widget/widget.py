""" This module contains the custom widget used in labnote """

# Python import

# PyQt import
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Project import
from labnote.core import stylesheet


class NoEntryWidget(QWidget):
    """Widget that indicate that no entry is selected """

    def __init__(self):
        super(NoEntryWidget, self).__init__()
        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/widget/no_entry_widget.qss")

        # Setting up the widget
        no_entry_pixmap = QPixmap(":/Icons/MainWindow/icons/main-window/no_entry_selected.png")
        lbl_no_entry_image = QLabel()
        lbl_no_entry_image.setAlignment(Qt.AlignCenter)

        lbl_no_entry_image.setPixmap(no_entry_pixmap.scaled(16, 16, Qt.KeepAspectRatio))

        lbl_no_entry = QLabel("No entry selected")
        lbl_no_entry.setAlignment(Qt.AlignCenter)

        # Setting up the layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(lbl_no_entry_image)
        main_layout.addWidget(lbl_no_entry)
