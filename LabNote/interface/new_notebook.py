"""
This module contains classes that create a new notebook
"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtCore import QRegExp

from ui.ui_new_notebook import Ui_NewNotebook


class NewNotebook(QDialog, Ui_NewNotebook):
    """
    Class that show New Notebook dialog
    """

    def __init__(self):
        super(NewNotebook, self).__init__()
        self.setupUi(self)

        # Set picture
        notebook_image = QPixmap(":/Icons/NewNotebook/icons/new-notebook/1xnotebook.png")
        if self.devicePixelRatio() == 2:
            notebook_image = QPixmap(":/Icons/NewNotebook/icons/new-notebook/2xnotebook.png")
            notebook_image.setDevicePixelRatio(self.devicePixelRatio())

        self.lbl_picture.setPixmap(notebook_image)

        # Set notebook name validator
        validator = QRegExpValidator(QRegExp("^[0-9a-zA-ZÀ-ÿ -._]+$"))
        self.txt_name.setValidator(validator)

        # Instance variable that contain the notebook name
        self.notebook_name = ""

        # Connect slots
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_create.clicked.connect(self.accept)
        self.txt_name.textChanged.connect(self.check_notebook_name)

    def check_notebook_name(self, text):
        if text != "":
            self.btn_create.setEnabled(True)
        else:
            self.btn_create.setEnabled(False)
        self.notebook_name = text