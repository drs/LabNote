from PyQt5.QtWidgets import QWidget, QMenu, QAction
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument, QPixmap, QPainter, QIcon, QPainterPath, QPen, QColor, \
    QTextListFormat, QBrush
from PyQt5.QtCore import Qt, QRectF

from ui.ui_textbox import Ui_TextBox
from common import stylesheet, color
from resources import resources


class Textbox(QWidget, Ui_TextBox):
    """
    Textbox widget class

    The textbox widget is a mini text editor that is used to edit protocols and experiments
    """
    def __init__(self):
        super(Textbox, self).__init__()
        self.setupUi(self)

        # Set button groups
        self.btn_bold.setProperty("Menu", False)
        self.btn_italic.setProperty("Menu", False)
        self.btn_underline.setProperty("Menu", False)
        self.btn_strikethrough.setProperty("Menu", False)
        self.btn_superscript.setProperty("Menu", False)
        self.btn_subscript.setProperty("Menu", False)
        self.btn_style.setProperty("Menu", True)
        self.btn_color.setProperty("Menu", True)
        self.btn_highlight.setProperty("Menu", True)
        self.btn_list.setProperty("Menu", True)
        self.btn_color.setProperty("IconOnly", True)
        self.btn_highlight.setProperty("IconOnly", True)

        # Style menu
        self.act_part = QAction("Part", self)
        self.act_part.setFont(QFont(self.font().family(), 20, 75))
        self.act_section = QAction("Section", self)
        self.act_section.setFont(QFont(self.font().family(), 16, 75))
        self.act_subsection = QAction("Subsection", self)
        self.act_subsection.setFont(QFont(self.font().family(), 14, 75))
        self.act_subsubsection = QAction("Subsubsection", self)
        self.act_subsubsection.setFont(QFont(self.font().family(), 12, 75))
        self.act_body = QAction("Body", self)
        self.act_body.setFont(QFont(self.font().family(), 12, 50))
        self.act_note = QAction("Note", self)
        self.act_note.setFont(QFont(self.font().family(), 10, 50))

        self.style_menu = QMenu(self)
        self.style_menu.addAction(self.act_part)
        self.style_menu.addAction(self.act_section)
        self.style_menu.addAction(self.act_subsection)
        self.style_menu.addAction(self.act_subsubsection)
        self.style_menu.addAction(self.act_body)
        self.style_menu.addAction(self.act_note)
        self.btn_style.setMenu(self.style_menu)

        # Highlight color menu
        self.act_clear_highlight = QAction("Clear", self)
        clear_highlight_icon = self.draw_color(Qt.white, Qt.lightGray)
        self.act_clear_highlight.setIcon(clear_highlight_icon)

        self.act_red_highlight = QAction("Red", self)
        red_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['red'].color, color.HIGHLIGHT_COLOR['red'].dark_shade)
        self.act_red_highlight.setIcon(red_highlight_icon)

        self.act_orange_highlight = QAction("Orange", self)
        orange_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['orange'].color, color.HIGHLIGHT_COLOR['orange'].dark_shade)
        self.act_orange_highlight.setIcon(orange_highlight_icon)

        self.act_yellow_highlight = QAction("Yellow", self)
        yellow_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['yellow'].color, color.HIGHLIGHT_COLOR['yellow'].dark_shade)
        self.act_yellow_highlight.setIcon(yellow_highlight_icon)

        self.act_green_highlight = QAction("Green", self)
        green_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['green'].color, color.HIGHLIGHT_COLOR['green'].dark_shade)
        self.act_green_highlight.setIcon(green_highlight_icon)

        self.act_blue_highlight = QAction("Blue", self)
        blue_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['blue'].color, color.HIGHLIGHT_COLOR['blue'].dark_shade)
        self.act_blue_highlight.setIcon(blue_highlight_icon)

        self.act_purple_highlight = QAction("Purple", self)
        purple_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['purple'].color, color.HIGHLIGHT_COLOR['purple'].dark_shade)
        self.act_purple_highlight.setIcon(purple_highlight_icon)

        self.act_gray_highlight = QAction("Gray", self)
        gray_highlight_icon = self.draw_color(color.HIGHLIGHT_COLOR['gray'].color, color.HIGHLIGHT_COLOR['gray'].dark_shade)
        self.act_gray_highlight.setIcon(gray_highlight_icon)

        self.highlight_menu = QMenu(self)
        self.highlight_menu.addAction(self.act_clear_highlight)
        self.highlight_menu.addAction(self.act_red_highlight)
        self.highlight_menu.addAction(self.act_orange_highlight)
        self.highlight_menu.addAction(self.act_yellow_highlight)
        self.highlight_menu.addAction(self.act_green_highlight)
        self.highlight_menu.addAction(self.act_blue_highlight)
        self.highlight_menu.addAction(self.act_purple_highlight)
        self.highlight_menu.addAction(self.act_gray_highlight)
        self.btn_highlight.setMenu(self.highlight_menu)

        # Text color menu
        self.act_black_text = QAction("Black", self)
        black_text_icon = self.draw_color(color.TEXT_COLOR['black'].color, color.TEXT_COLOR['black'].dark_shade)
        self.act_black_text.setIcon(black_text_icon)

        self.act_gray_text = QAction("Gray", self)
        gray_text_icon = self.draw_color(color.TEXT_COLOR['gray'].color, color.TEXT_COLOR['gray'].dark_shade)
        self.act_gray_text.setIcon(gray_text_icon)

        self.act_red_text = QAction("Red", self)
        red_text_icon = self.draw_color(color.TEXT_COLOR['red'].color, color.TEXT_COLOR['red'].dark_shade)
        self.act_red_text.setIcon(red_text_icon)

        self.act_orange_text = QAction("Orange", self)
        orange_text_icon = self.draw_color(color.TEXT_COLOR['orange'].color, color.TEXT_COLOR['orange'].dark_shade)
        self.act_orange_text.setIcon(orange_text_icon)

        self.act_yellow_text = QAction("Yellow", self)
        yellow_text_icon = self.draw_color(color.TEXT_COLOR['yellow'].color, color.TEXT_COLOR['yellow'].dark_shade)
        self.act_yellow_text.setIcon(yellow_text_icon)

        self.act_green_text = QAction("Green", self)
        green_text_icon = self.draw_color(color.TEXT_COLOR['green'].color, color.TEXT_COLOR['green'].dark_shade)
        self.act_green_text.setIcon(green_text_icon)

        self.act_blue_text = QAction("Blue", self)
        blue_text_icon = self.draw_color(color.TEXT_COLOR['blue'].color, color.TEXT_COLOR['blue'].dark_shade)
        self.act_blue_text.setIcon(blue_text_icon)

        self.act_purple_text = QAction("Purple", self)
        purple_text_icon = self.draw_color(color.TEXT_COLOR['purple'].color, color.TEXT_COLOR['purple'].dark_shade)
        self.act_purple_text.setIcon(purple_text_icon)

        self.color_menu = QMenu(self)
        self.color_menu.addAction(self.act_black_text)
        self.color_menu.addAction(self.act_gray_text)
        self.color_menu.addAction(self.act_red_text)
        self.color_menu.addAction(self.act_orange_text)
        self.color_menu.addAction(self.act_yellow_text)
        self.color_menu.addAction(self.act_green_text)
        self.color_menu.addAction(self.act_blue_text)
        self.color_menu.addAction(self.act_purple_text)
        self.btn_color.setMenu(self.color_menu)

        # List menu
        self.act_no_list = QAction("No list", self)
        self.act_bullet_list = QAction("•  Bullet", self)
        self.act_numbered_list = QAction("1. Numbered", self)
        self.act_roman_list = QAction("I.  Roman numbered", self)
        self.act_uppercase_list = QAction("A. Uppercase letters", self)
        self.act_lowercase_list = QAction("a. Lowercase letters", self)
        self.act_increase_indent = QAction("Increase indentation")
        self.act_decrease_indent = QAction("Decrease indentation")

        self.list_menu = QMenu(self)
        self.list_menu.addAction(self.act_no_list)
        self.list_menu.addAction(self.act_bullet_list)
        self.list_menu.addAction(self.act_numbered_list)
        self.list_menu.addAction(self.act_roman_list)
        self.list_menu.addAction(self.act_uppercase_list)
        self.list_menu.addAction(self.act_lowercase_list)
        self.list_menu.addSeparator()
        self.list_menu.addAction(self.act_increase_indent)
        self.list_menu.addAction(self.act_decrease_indent)

        self.btn_list.setMenu(self.list_menu)

        # Set style sheet
        stylesheet.set_style_sheet(self, ":/StyleSheet/style-sheet/textbox.qss")

        # Superscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sup>&thinsp;2</sup></p>")

        pixmap = self.draw_text(text)
        icon = QIcon(pixmap)
        self.btn_superscript.setIcon(icon)
        self.btn_superscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Subscript button text
        text = QTextDocument()
        text.setHtml("<p style = color:#484848 >X<sub>&thinsp;2</sub></p>")

        pixmap = self.draw_text(text)
        icon = QIcon(pixmap)
        self.btn_subscript.setIcon(icon)
        self.btn_subscript.setIconSize(pixmap.rect().size() / self.devicePixelRatioF())

        # Default color icons
        self.change_highlight_button_icon(self.act_clear_highlight)
        self.change_text_color_button_icon(self.act_black_text)
        self.change_list_button_icon(self.act_no_list)

        # Slots connection
        self.btn_bold.clicked.connect(self.format_bold)
        self.btn_italic.clicked.connect(self.format_italic)
        self.btn_underline.clicked.connect(self.format_underline)
        self.btn_strikethrough.clicked.connect(self.format_strikethrough)
        self.btn_superscript.clicked.connect(self.format_superscript)
        self.btn_subscript.clicked.connect(self.format_subscript)
        self.highlight_menu.triggered.connect(self.change_highlight_button_icon)
        self.color_menu.triggered.connect(self.change_text_color_button_icon)
        self.list_menu.triggered.connect(self.change_list_button_icon)
        self.list_menu.triggered.connect(self.format_list)
        self.color_menu.triggered.connect(self.format_text_color)
        self.highlight_menu.triggered.connect(self.format_highlight)
        self.style_menu.triggered.connect(self.format_style)
        self.textEdit.cursorPositionChanged.connect(self.update_button)

    def change_list_button_icon(self, action):
        """Change the list button icon to the selected list format

        :param action: Selected action.
        :type action: QAction
        """

        # Ignore the indent change action when changing the icon type
        if not (action == self.act_increase_indent or action == self.act_decrease_indent):
            if action == self.act_bullet_list:
                icon = self.draw_list(["•", "•", "•"])
            elif action == self.act_numbered_list:
                icon = self.draw_list(["1.", "2.", "3."])
            elif action == self.act_roman_list:
                icon = self.draw_list(["I.", "II.", "III."])
            elif action == self.act_uppercase_list:
                icon = self.draw_list(["A.", "B.", "C."])
            else:
                icon = self.draw_list(["a.", "b.", "c."])
            self.btn_list.setIcon(icon)

            # Do no check the button is no list is selected
            if not (action == self.act_no_list):
                self.btn_list.setChecked(True)
            elif action == self.act_no_list:
                self.btn_list.setChecked(False)

    def draw_list(self, separator_list):
        """Draw the list icons for the icon menu

        .. note::
            This function handle HiDPI as well a regular screen

        :param separator_list: List of the bullets
        :type separator_list: List[str]
        :returns:  QPixmap -- Icon pixmap
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(16 * dpr, 16 * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent) # Required to create a transparent background

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        painter.setFont(QFont(self.font().family(), 5, 50))
        pen = QPen(QColor(72, 72, 72), 1)
        painter.setPen(pen)
        painter.drawLine(7, 3, 15, 3)
        painter.drawText(0, 0, 32, 22, Qt.AlignLeft, separator_list[0])
        painter.drawLine(7, 8, 15, 8)
        painter.drawText(0, 5, 32, 22, Qt.AlignLeft, separator_list[1])
        painter.drawLine(7, 13, 15, 13)
        painter.drawText(0, 10, 32, 22, Qt.AlignLeft, separator_list[2])
        painter.end()

        return QIcon(pixmap)

    def change_text_color_button_icon(self, action):
        """Change the text color button icon to the selected color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_gray_text:
            icon = self.draw_color(color.TEXT_COLOR['gray'].color, color.TEXT_COLOR['gray'].dark_shade)
        elif action == self.act_red_text:
            icon = self.draw_color(color.TEXT_COLOR['red'].color, color.TEXT_COLOR['red'].dark_shade)
        elif action == self.act_orange_text:
            icon = self.draw_color(color.TEXT_COLOR['orange'].color, color.TEXT_COLOR['orange'].dark_shade)
        elif action == self.act_yellow_text:
            icon = self.draw_color(color.TEXT_COLOR['yellow'].color, color.TEXT_COLOR['yellow'].dark_shade)
        elif action == self.act_green_text:
            icon = self.draw_color(color.TEXT_COLOR['green'].color, color.TEXT_COLOR['green'].dark_shade)
        elif action == self.act_blue_text:
            icon = self.draw_color(color.TEXT_COLOR['blue'].color, color.TEXT_COLOR['blue'].dark_shade)
        elif action == self.act_purple_text:
            icon = self.draw_color(color.TEXT_COLOR['purple'].color, color.TEXT_COLOR['purple'].dark_shade)
        else:
            icon = self.draw_color(color.TEXT_COLOR['black'].color, color.TEXT_COLOR['black'].dark_shade)
        self.btn_color.setIcon(icon)

    def change_highlight_button_icon(self, action):
        """Change the highlight button icon to the selected color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_red_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['red'].color, color.HIGHLIGHT_COLOR['red'].dark_shade)
        elif action == self.act_orange_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['orange'].color, color.HIGHLIGHT_COLOR['orange'].dark_shade)
        elif action == self.act_yellow_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['yellow'].color, color.HIGHLIGHT_COLOR['yellow'].dark_shade)
        elif action == self.act_green_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['green'].color, color.HIGHLIGHT_COLOR['green'].dark_shade)
        elif action == self.act_blue_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['blue'].color, color.HIGHLIGHT_COLOR['blue'].dark_shade)
        elif action == self.act_purple_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['purple'].color, color.HIGHLIGHT_COLOR['purple'].dark_shade)
        elif action == self.act_gray_highlight:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['gray'].color, color.HIGHLIGHT_COLOR['gray'].dark_shade)
        else:
            icon = self.draw_color(color.HIGHLIGHT_COLOR['clear'].color, color.HIGHLIGHT_COLOR['clear'].dark_shade)
        self.btn_highlight.setIcon(icon)

    def draw_color(self, fill, border):
        """Draw the color icons for the highlight and the text color menu

        :param fill: Fill color.
        :type fill: QColor
        :param border: Border color.
        :type border: QColor
        :returns:  QPixmap -- Icon pixmap
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(16 * dpr, 16 * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, 12, 12), 2, 2)

        pen = QPen(border, 1)
        painter.setPen(pen)
        painter.fillPath(path, fill)
        painter.drawPath(path)
        painter.end()

        return QIcon(pixmap)

    def draw_text(self, text):
        """Draw an icon from a html text and return it as a pixmap.

        .. note::
            This function handle HiDPI as well a regular screen.

        :param text: QTextDocument with HTML code for the icon.
        :type text: QTextDocument
        :returns:  QPixmap -- Returns pixmap that can be used to create the icon

        .. note::
            Unlike the other drawing function, this function return a pixel map. As of now, this is required to create
            a good sized icon. This should therefore not be changed unless the the output icon size is right (it is
            currently too small).
        """
        # Create a base pixmap
        # Set the pixmap pixel ratio so that the image looks good in normal as well as HiDPI screens
        dpr = self.devicePixelRatioF()
        pixmap = QPixmap(text.size().width() * dpr, text.size().height() * dpr)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.transparent)

        # Paint the elements of the icon
        painter = QPainter(pixmap)
        text.drawContents(painter, QRectF(pixmap.rect()))
        painter.end()

        return pixmap

    def merge_format_on_word_or_selection(self, fmt):
        """ Change the caracter format when a format button is pressed.

        The font is changed for the selection or from the cursor position.
        :param fmt: Text format
        """
        cursor = self.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.textEdit.mergeCurrentCharFormat(fmt)

    def format_bold(self):
        """ Set text format to bold. """
        fmt = QTextCharFormat()
        if self.btn_bold.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_italic(self):
        """ Set text format to italic. """
        fmt = QTextCharFormat()
        if self.btn_italic.isChecked():
            fmt.setFontItalic(True)
        else:
            fmt.setFontItalic(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_underline(self):
        """ Set text format to underline. """
        fmt = QTextCharFormat()
        if self.btn_underline.isChecked():
            fmt.setFontUnderline(True)
        else:
            fmt.setFontUnderline(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_strikethrough(self):
        """ Set text format to strikethrough. """
        fmt = QTextCharFormat()
        if self.btn_strikethrough.isChecked():
            fmt.setFontStrikeOut(True)
        else:
            fmt.setFontStrikeOut(False)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_superscript(self):
        """ Set text vertical alignment to superscript. """
        fmt = QTextCharFormat()
        if self.btn_superscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_subscript(self):
        """ Set text vertical alignment to subscript. """
        fmt = QTextCharFormat()
        if self.btn_subscript.isChecked():
            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_list(self, action):
        """ set list format according to selected format

        :param action: Selected action.
        :type action: QAction
        """

        # Create a new list
        if not (action == self.act_increase_indent or action == self.act_decrease_indent or action == self.act_no_list):
            # Set the list type format
            fmt = QTextListFormat()
            if action == self.act_bullet_list:
                fmt.setStyle(QTextListFormat.ListDisc)
            elif action == self.act_numbered_list:
                fmt.setStyle(QTextListFormat.ListDecimal)
            elif action == self.act_roman_list:
                fmt.setStyle(QTextListFormat.ListUpperRoman)
            elif action == self.act_uppercase_list:
                fmt.setStyle(QTextListFormat.ListUpperAlpha)
            else:
                fmt.setStyle(QTextListFormat.ListLowerAlpha)

            # Add the list to the the text edit
            cursor = self.textEdit.textCursor()
            cursor.createList(fmt)
        # Delete an existing list
        elif action == self.act_no_list:
            # Get the current list
            cursor = self.textEdit.textCursor()
            current_list = cursor.currentList()
            current_block = cursor.block()

            # Remove the list
            current_list.remove(current_block)

            # Restore indent
            fmt = cursor.blockFormat()
            fmt.setIndent(0)
            cursor.setBlockFormat(fmt)
        # Change the indent
        else:
            cursor = self.textEdit.textCursor()
            current_format = cursor.currentList().format()
            current_indent = current_format.indent()

            new_indent = 0
            if action == self.act_increase_indent:
                new_indent = current_indent + 1
            else:
                new_indent = current_indent - 1

            new_format = current_format
            new_format.setIndent(new_indent)
            cursor.createList(new_format)

    def format_text_color(self, action):
        """ Set the text color

        :param action: Selected action.
        :type action: QAction
        """
        if action == self.act_gray_text:
            color = QColor(196, 196, 196)
        elif action == self.act_red_text:
            color = QColor(150, 16, 16)
        elif action == self.act_orange_text:
            color = QColor(211, 116, 0)
        elif action == self.act_yellow_text:
            color = QColor(229, 221, 0)
        elif action == self.act_green_text:
            color = QColor(34, 139, 34)
        elif action == self.act_blue_text:
            color = QColor(18, 18, 130)
        elif action == self.act_purple_text:
            color = QColor(117, 21, 117)
        else:
            color = Qt.black

        fmt = QTextCharFormat()
        fmt.setForeground(QBrush(color))
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_highlight(self, action):
        """ Set the highlight color

        .. note::
            The highlight color alpha channel is set to 128 so the color are semi-transparent. This prevent the colors
            to be too harsh.

        :param action: Selected action.
        :type action: QAction
        """
        fmt = QTextCharFormat()

        # Set the selected color to background
        if not action == self.act_clear_highlight:
            if action == self.act_red_highlight:
                color = QColor(242, 41, 74, 128)
            elif action == self.act_orange_highlight:
                color = QColor(252, 116, 42, 128)
            elif action == self.act_yellow_highlight:
                color = QColor(255, 251, 45, 128)
            elif action == self.act_green_highlight:
                color = QColor(0, 250, 154, 128)
            elif action == self.act_blue_highlight:
                color = QColor(49, 170, 226, 128)
            elif action == self.act_purple_highlight:
                color = QColor(155, 71, 229, 128)
            else:
                color = QColor(196, 196, 196, 128)

            fmt.setBackground(QBrush(color))
        # Remove the background
        else:
            fmt.clearBackground()
        self.merge_format_on_word_or_selection(fmt=fmt)

    def format_style(self, action):
        """ Set a predefined format on the selected text

        :param action: Selected action (format).
        :type action: QAction
        """
        fmt = QTextCharFormat()

        # Define the format according to the selected style
        if action == self.act_part:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(20)
        elif action == self.act_section:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(16)
        elif action == self.act_subsection:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(14)
        elif action == self.act_subsubsection:
            fmt.setFontWeight(75)
            fmt.setFontPointSize(12)
        elif action == self.act_body:
            fmt.setFontWeight(50)
            fmt.setFontPointSize(12)
        elif action == self.act_note:
            fmt.setFontWeight(50)
            fmt.setFontPointSize(10)

        # Define the format common to every style
        fmt.setForeground(QBrush(Qt.black))
        fmt.clearBackground()
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setFontStrikeOut(False)
        fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        self.merge_format_on_word_or_selection(fmt=fmt)

    def update_button(self):
        """ Set the button states to match the selected text format """

        # Get text format
        cfmt = self.textEdit.textCursor().charFormat()

        # Bold button
        if cfmt.fontWeight() == 75:
            self.btn_bold.setChecked(True)
        else:
            self.btn_bold.setChecked(False)

        # Italic button
        if cfmt.fontItalic():
            self.btn_italic.setChecked(True)
        else:
            self.btn_italic.setChecked(False)

        # Underline button
        if cfmt.fontUnderline():
            self.btn_underline.setChecked(True)
        else:
            self.btn_underline.setChecked(False)

        # Strikethrough button
        if cfmt.fontStrikeOut():
            self.btn_strikethrough.setChecked(True)
        else:
            self.btn_strikethrough.setChecked(False)

        # Superscript button
        if cfmt.verticalAlignment() == QTextCharFormat.AlignSuperScript:
            self.btn_superscript.setChecked(True)
        else:
            self.btn_superscript.setChecked(False)

        # Subscript button
        if cfmt.verticalAlignment() == QTextCharFormat.AlignSubScript:
            self.btn_subscript.setChecked(True)
        else:
            self.btn_subscript.setChecked(False)

        # Get color format
        # Background color
        background_color = cfmt.background().color()
        if background_color.rgb() == color.HIGHLIGHT_COLOR['red'].color.rgb():
            self.change_highlight_button_icon(self.act_red_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['orange'].color.rgb():
            self.change_highlight_button_icon(self.act_orange_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['yellow'].color.rgb():
            self.change_highlight_button_icon(self.act_yellow_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['green'].color.rgb():
            self.change_highlight_button_icon(self.act_green_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['blue'].color.rgb():
            self.change_highlight_button_icon(self.act_blue_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['purple'].color.rgb():
            self.change_highlight_button_icon(self.act_purple_highlight)
        elif background_color.rgb() == color.HIGHLIGHT_COLOR['gray'].color.rgb():
            self.change_highlight_button_icon(self.act_gray_highlight)
        else:
            self.change_highlight_button_icon(self.act_clear_highlight)

        # Text color
        text_color = cfmt.foreground().color()

        if text_color == color.TEXT_COLOR['gray'].color:
            self.change_text_color_button_icon(self.act_gray_text)
        elif text_color == color.TEXT_COLOR['red'].color:
            self.change_text_color_button_icon(self.act_red_text)
        elif text_color == color.TEXT_COLOR['orange'].color:
            self.change_text_color_button_icon(self.act_orange_text)
        elif text_color == color.TEXT_COLOR['yellow'].color:
            self.change_text_color_button_icon(self.act_yellow_text)
        elif text_color == color.TEXT_COLOR['gray'].color:
            self.change_text_color_button_icon(self.act_gray_text)
        elif text_color == color.TEXT_COLOR['green'].color:
            self.change_text_color_button_icon(self.act_green_text)
        elif text_color == color.TEXT_COLOR['blue'].color:
            self.change_text_color_button_icon(self.act_blue_text)
        elif text_color == color.TEXT_COLOR['purple'].color:
            self.change_text_color_button_icon(self.act_purple_text)
        else:
            self.change_text_color_button_icon(self.act_black_text)

        # Get list format
        if self.textEdit.textCursor().currentList():
            self.btn_list.setChecked(True)
        else:
            self.btn_list.setChecked(False)
