""" This module contains all the models used in labnote """

# Python import

# PyQt import
from PyQt5.QtGui import QStandardItemModel

# Project import


class StandardItemModel(QStandardItemModel):
    """ Custom standard item model class """
    def get_persistant_index_list(self):
        return self.persistentIndexList()