""" This module contains all the custom LineEdit used in LabNote """

# PyQt import
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator


class LineEdit(QLineEdit):
    """ Lineedit used in the form """
    def __init__(self):
        super(LineEdit, self).__init__()
        self.setAttribute(Qt.WA_MacShowFocusRect, 0)


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