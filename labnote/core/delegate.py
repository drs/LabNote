""" This module contains the specialised delegates """

# PyQt import
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem, QProxyStyle


class NoFocusDelegate(QStyledItemDelegate):
    """ This delegate remove the blue focus rectangle for tableviewitem"""
    def paint(self, painter, style_option, index):
        option = QStyleOptionViewItem(style_option)
        if option.state & QStyle.State_HasFocus:
            option.state = option.state ^ QStyle.State_HasFocus
        QStyledItemDelegate().paint(painter, option, index)


class StyleTweak(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        print(element)
        if element == QStyle.PE_FrameFocusRect:
            return

        QProxyStyle().drawPrimitive(element, option, painter, widget)
