""" This module contains QObject subclasses used in LabNote """

# Python import

# PyQt import
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import Qt, QStringListModel, QRegExp
from PyQt5.QtGui import QRegExpValidator

# Project import


class SearchCompleter(QCompleter):
    """ This is the subclass of completer that is used in search """

    def __init__(self, completer_list):
        super(SearchCompleter, self).__init__()

        self.setModel(QStringListModel(completer_list))
        self.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setWrapAround(False)
        self.setCompletionMode(QCompleter.PopupCompletion)

    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index)
        lst = str(self.widget().text().split(','))

        if len(lst) > 1:
            path = '{}, {}'.format(','.join(lst[:-1]), path)

        return path

    def splitPath(self, path):
        path = str(path.split(',')[:-1]).lstrip(' ')
        return [path]


class NameValidator(QRegExpValidator):
    """ RegExpValidator subclass used for the names """
    def __init__(self):
        super(NameValidator, self).__init__()
        self.setRegExp(QRegExp("^[0-9a-zA-ZÀ-ÿ -._]+$"))


class KeyValidator(QRegExpValidator):
    """ RegExpValidator subclass used for the key """
    def __init__(self):
        super(KeyValidator, self).__init__()
        self.setRegExp(QRegExp("^[a-z]{1}[0-9a-z_-]+$"))
