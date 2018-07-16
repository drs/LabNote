""" This module contains the layout management functions """

# Python import
import sip


def empty_layout(obj, layout):
    """ Empty any layout

    :param obj: Object that contains the layout
    :type obj: QObject
    :param layout: Layout to be emptied
    :type layout: QLayout
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                delete_layout(item.layout())


def delete_layout(self, layout):
    """ Delete any layout """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.delete_layout(item.layout())
        sip.delete(layout)


def disable_layout(layout, enable):
    """ Set enable state for all items in layout

    :param layout: Layout
    :type layout: QLayout
    :param enable: Enable state
    :type enable: bool
    """
    for position in range(0, layout.count()):
        item = layout.itemAt(position)

        # Disable widget
        widget = item.widget()
        if widget:
            widget.setEnabled(enable)

        # Disable layout
        sub_layout = item.layout()
        if sub_layout:
            disable_layout(sub_layout, enable)
