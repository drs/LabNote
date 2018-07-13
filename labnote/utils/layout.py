""" This module contains the layout management functions """


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
                obj.delete_layout(item.layout())
