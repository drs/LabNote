""" This module contains all the constant value used in labnote """

# PyQt import
from PyQt5.QtCore import Qt

"""
Type value
"""

# Reference type
TYPE_ARTICLE = 0
TYPE_BOOK = 1
TYPE_CHAPTER = 2

# Category frame content type
TYPE_LIBRARY = 48
TYPE_PROTOCOL = 49

"""
Data level
"""

# Data type
QT_LevelRole = Qt.UserRole+1
QT_StateRole = QT_LevelRole+1

# Level type
LEVEL_CATEGORY = 101
LEVEL_SUBCATEGORY = 102
LEVEL_ENTRY = 103