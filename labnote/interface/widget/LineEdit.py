""" This module contains all the custom LineEdit used in LabNote """

# PyQt import
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIcon

# Project import
from labnote.core import stylesheet
from labnote.interface.widget.object import SearchCompleter


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
        stylesheet.set_style_sheet(self, ":/StyleSheet/Widget/style-sheet/widget/search.qss")
        

class TagSearchLineEdit(SearchLineEdit):
    """ Search line edit with the tag completer """

    completer = None

    def __init__(self, tag_list):
        super(TagSearchLineEdit, self).__init__()
        self.setCompleter(SearchCompleter(tag_list))
        self.setValidator(QRegExpValidator(QRegExp("^([0-9a-zA-z_-]+[, ]{2})+$")))

    def keyPressEvent(self, event):
        # Process event normally
        QLineEdit.keyPressEvent(self, event)
        
        # Handle the completer
        if not self.completer:
            return

        self.completer.setCompletionPrefix(self.cursorWord(self.text()))
        if len(self.completer.completionPrefix()) < 1:
            self.completer.popup().hide()
            return

        rect = self.cursorRect()
        rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                      self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete()

    def cursorWord(self, sentence):
        return sentence[sentence.rfind(' ')+1:]

    def setCompleter(self, completer):
        self.completer = completer
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        self.setText(self.text().replace(self.text()[self.text().rfind(','):], completion))


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
