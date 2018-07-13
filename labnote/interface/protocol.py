""" This module contains the protocol dialog classes """

# Python import

# PyQt import
from PyQt5.QtWidgets import QDialog

# Project import
from labnote.ui.ui_protocol import Ui_Protocol
from labnote.interface.widget.lineedit import SearchLineEdit
from labnote.interface.widget.widget import CategoryFrame
from labnote.interface.textbox import TextEdit
from labnote.core import labnote, stylesheet


class Protocol(QDialog, Ui_Protocol):
    """ Class responsible of managing the protocol window interface """
    def __init__(self, parent=None):
        super(Protocol, self).__init__(parent=parent)
        # Initialize the GUI
        self.setupUi(self)
        self.init_ui()
        self.init_connection()

        self.show()

    def init_ui(self):
        # Show category frame
        self.category_frame = CategoryFrame('Protocol', labnote.TYPE_PROTOCOL)
        self.frame.layout().insertWidget(0, self.category_frame)

        # Show search button
        self.txt_search = SearchLineEdit()
        self.layout_search.insertWidget(2, self.txt_search)

        # Show textedit
        self.textedit = TextEdit()
        self.frame.layout().insertWidget(1, self.textedit)
        self.frame.layout().setStretch(1, 10)

        # Set stylesheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/protocol.qss")

    def init_connection(self):
        self.btn_close.clicked.connect(self.close)