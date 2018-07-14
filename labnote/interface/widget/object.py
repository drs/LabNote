""" This module contains QObject subclasses used in LabNote """

# Python import

# PyQt import
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import Qt, QStringListModel

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