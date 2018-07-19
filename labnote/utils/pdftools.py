# Python import
from datetime import datetime

# PyQt import
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextTableFormat, QTextLength, QTextCharFormat, QBrush
from PyQt5.QtCore import Qt


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

    cursor.insertHtml("""<center><font size="3"><b>{}</b></font></center>""".format(title))
    cursor.insertHtml("<br>")
    table_format = QTextTableFormat()
    table_format.setCellSpacing(0)
    table_format.setWidth(QTextLength(QTextLength.PercentageLength, 100))
    table_format.setBorderBrush(QBrush(Qt.SolidPattern))

    table_char_fmt = QTextCharFormat()
    table_char_fmt.setFontPointSize(10.5)

    table = cursor.insertTable(2, 2, table_format)
    table.mergeCells(1, 0, 1, 2)
    cursor.insertText("Document : {}\n".format(key), table_char_fmt)
    cursor.movePosition(cursor.NextCell)
    cursor.insertText("Created : {}".format(date), table_char_fmt)
    if update:
        cursor.insertText("\nLast update : {}".format(update), table_char_fmt)
    cursor.movePosition(cursor.NextCell)
    cursor.insertText("Author : Samuel Drouin - Lallemand Animal Nutrition", table_char_fmt)

    cursor.movePosition(cursor.End)
    html_start = cursor.position()

    cursor.insertHtml("<br>")

    cursor.insertHtml(body)

    # Change the font family
    fmt = QTextCharFormat()
    fmt.setFontFamily('Verdana')

    cursor.setPosition(0)
    cursor.movePosition(cursor.End, QTextCursor.KeepAnchor)
    cursor.mergeCharFormat(fmt)

    # Make the font smaller everywhere and remove the anchors
    position = html_start
    cursor.setPosition(position)
    while not cursor.atEnd():
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)

        char_fmt = cursor.charFormat()
        if cursor.charFormat().isAnchor():
            char_fmt.setAnchor(False)
            char_fmt.setFontUnderline(False)
            char_fmt.setForeground(Qt.black)

        if cursor.charFormat().fontPointSize() > 0:
            char_fmt.setFontPointSize(cursor.charFormat().fontPointSize() - 3)
        if cursor.charFormat().fontPointSize() == 10:
            char_fmt.setFontPointSize(8)
        cursor.mergeCharFormat(char_fmt)

        position = position + 1

    return cursor.document().toHtml()
