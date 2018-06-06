from PyQt5.QtCore import QFile, QTextStream


def set_style_sheet(qobject, file):
    # Set style sheet
    qss = QFile(file)
    qss.open(QFile.ReadOnly)
    style = QTextStream(qss).readAll()
    qobject.setStyleSheet(style)
    qss.close()
