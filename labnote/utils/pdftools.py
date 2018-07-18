# Python import
from datetime import datetime

# PyQt import
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextTableFormat, QTextBlockFormat, QTextCharFormat, QFont, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter


def prepare_html_pdf(title, key, date, update, body):
    """ Generate the HTML document

    :param title: Document title
    :type title: str
    :param key: Document key
    :type key: str
    :param date: Date created
    :type date: str
    :param update: Date updated
    :type update: str
    :param body: Text document body
    :type body: str
    """

    # Open the document
    document = QTextDocument()
    cursor = QTextCursor(document)
    cursor.setPosition(0)

    cursor.insertHtml("""<center<font size="5">{}</font></center>""".format(title))
    cursor.insertHtml("<br>")
    table_format = QTextTableFormat()
    table_format.setCellSpacing(0)
    table_format.setBorderBrush(QBrush(Qt.SolidPattern))

    table = cursor.insertTable(2, 2, table_format)
    table.mergeCells(1, 0, 1, 2)
    cursor.insertText("Document : {}".format(key))
    cursor.movePosition(cursor.NextCell)
    cursor.insertText("Created : {}".format(format_datetime(date)))
    if update:
        cursor.insertText("\nLast update : {}".format(format_datetime(update)))
    cursor.movePosition(cursor.NextCell)
    cursor.insertText("Author : Samuel Drouin - Lallemand Animal Nutrition")

    cursor.movePosition(cursor.End)

    cursor.insertHtml("<br>")

    cursor.insertHtml(body)

    return cursor.document().toHtml()


def format_datetime(dt):
    """ Format datetime """
    date = datetime.strptime(dt, '%Y-%m-%d %H:%M')
    return date.strftime('%B %e, %Y')
