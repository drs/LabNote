# PyQt import
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLayout

# Project import
from LabNote.resources import resources
from LabNote.common import stylesheet


class ListWidget(QWidget):
    def __init__(self):
        super(ListWidget, self).__init__()

        # Set widgets
        self.lbl_title = QLabel()
        self.lbl_subtitle = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_subtitle)
        layout.addStretch()
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

    def set_title(self, title):
        self.lbl_title.setText(title)

    def set_subtitle(self, subtitle):
        self.subtitle.setText(subtitle)
