from collections import namedtuple

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

Color = namedtuple('Color', ['color', 'dark_shade'])

WHITE = Color(Qt.white, Qt.lightGray)
BLACK = Color(Qt.black, Qt.black)
GRAY = Color(QColor(196, 196, 196), QColor(142, 142, 142))
RED = Color(QColor(242, 41, 74), QColor(193, 32, 59))
DARK_RED = Color(QColor(150, 16, 16), QColor(109, 12, 12))
ORANGE = Color(QColor(252, 116, 42), QColor(188, 87, 32))
DARK_ORANGE = Color(QColor(211, 116, 0), QColor(155, 85, 0))
YELLOW = Color(QColor(255, 251, 45), QColor(186, 183, 33))
DARK_YELLOW = Color(QColor(229, 221, 0), QColor(175, 169, 0))
GREEN = Color(QColor(0, 250, 154), QColor(0, 173, 106))
DARK_GREEN = Color(QColor(34,139,34), QColor(22, 91, 22))
BLUE = Color(QColor(49, 170, 226), QColor(37, 126, 168))
DARK_BLUE = Color(QColor(18, 18, 130), QColor(11, 11, 79))
PURPLE = Color(QColor(155, 71, 229), QColor(111, 52, 163))
DARK_PURPLE = Color(QColor(117, 21, 117), QColor(71, 12, 71))

TEXT_COLOR = {
    'black': BLACK,
    'gray': GRAY,
    'red': DARK_RED,
    'orange': DARK_ORANGE,
    'yellow': DARK_YELLOW,
    'green': DARK_GREEN,
    'blue': DARK_BLUE,
    'purple': DARK_PURPLE
}

HIGHLIGHT_COLOR = {
    'clear': WHITE,
    'red': RED,
    'orange': ORANGE,
    'yellow': YELLOW,
    'green': GREEN,
    'blue': BLUE,
    'purple': PURPLE,
    'gray': GRAY
}