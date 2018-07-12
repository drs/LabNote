""" This module contains the classes that show the dataset dialog """

# Python import

# PyQt import
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

# Project import
from labnote.ui.ui_dataset import Ui_Dataset
from labnote.core import stylesheet
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.dialog import dataset


class Dataset(QDialog, Ui_Dataset):
    """ Class responsible of diplaying the dataset window interface """
    def __init__(self, parent=None):
        super(Dataset, self).__init__(parent)

        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        # Show the dialog
        self.show()

    def init_ui(self):
        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/dataset.qss")

        # Setup import button
        self.btn_import.setText("Import")
        icon = QIcon(":/Icon/Sample/icons/sample/import.png")
        icon.addFile(":/Icon/Sample/icons/sample/import_pressed.png", QSize(), QIcon.Normal, QIcon.On)
        self.btn_import.setIcon(icon)
        self.btn_import.setCheckable(True)
        self.btn_import.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Setup R button
        self.btn_r.setText("R Script")
        self.btn_r.setIcon(QIcon(":/Icon/Dataset/icons/dataset/r.png"))
        self.btn_r.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Setup R run button
        self.btn_r_run.setText("Run R Script")
        self.btn_r_run.setIcon(QIcon(":/Icon/Dataset/icons/dataset/r_run.png"))
        self.btn_r_run.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Setup python button
        self.btn_python.setText("Python")
        self.btn_python.setIcon(QIcon(":/Icon/Dataset/icons/dataset/python.png"))
        self.btn_python.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Setup python run button
        self.btn_python_run.setText("Run Python")
        self.btn_python_run.setIcon(QIcon(":/Icon/Dataset/icons/dataset/python_run.png"))
        self.btn_python_run.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Search lineedit
        self.txt_search = SearchLineEdit()
        self.layout_search.insertWidget(15, self.txt_search)

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)
        self.btn_add.clicked.connect(self.create_dataset)

    def create_dataset(self):
        """ Create a new dataset in the database """
        self.dataset_dialog = dataset.DatasetDialog()
        self.dataset_dialog.setWindowModality(Qt.WindowModal)
        self.dataset_dialog.setParent(self, Qt.Sheet)
        self.dataset_dialog.show()
        #self.notebook.accepted.connect(self.view_notebook.show_content)
