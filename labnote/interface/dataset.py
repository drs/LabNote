""" This module contains the classes that show the dataset dialog """

# Python import

# PyQt import
from PyQt5.QtWidgets import QDialog

# Project import
from labnote.ui.ui_dataset import Ui_Dataset


class Dataset(QDialog, Ui_Dataset):
    """ Class responsible of diplaying the dataset window interface """
    def __init__(self, parent=None):
        super(Dataset, self).__init__(parent)

        # Initialize the GUI
        self.setupUi(self)

        # Show the dialog
        self.show()