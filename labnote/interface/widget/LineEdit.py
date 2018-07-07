""" This module contains all the custom LineEdit used in LabNote """

# PyQt import
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon

# Project import
from labnote.core import stylesheet


class LineEdit(QLineEdit):
    """ Lineedit used in the form """
    def __init__(self):
        super(LineEdit, self).__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


class SearchLineEdit(LineEdit):
    """ Search line edit """
    def __init__(self):
        super(SearchLineEdit, self).__init__()
        self.setPlaceholderText("Search")

        # Set icon
        search_icon = QIcon(":/Icons/MainWindow/icons/main-window/search.png")
        self.addAction(search_icon, QLineEdit.LeadingPosition)
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/general/search.qss")


class YearLineEdit(LineEdit):
    """ Lineedit used for the year """
    def __init__(self):
        super(YearLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{4}$"))
        self.setValidator(validator)


class NumberLineEdit(LineEdit):
    """ Lineedit used in the number only fields """
    def __init__(self):
        super(NumberLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{5}$"))
        self.setValidator(validator)


class PagesLineEdit(LineEdit):
    """ Lineedit used for the pages """
    def __init__(self):
        super(PagesLineEdit, self).__init__()

        validator = QRegExpValidator(QRegExp("^[0-9]{0,5}( - |-)[0-9]{0,5}"))
        self.setValidator(validator)