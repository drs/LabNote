""" This module contains the class that handle data preparation """

# Python import
import uuid


"""
Database string format
"""


def prepare_string(string):
    """ Change empty string to None

    :param string: Text string
    :type string: str
    :return: str or None if the string is empty
    """

    if string == "":
        return None
    else:
        return string


def receive_string(value):
    """ Convert the value to string

    :param value: Value to convert to string
    :return str: String from value
    """
    if not value:
        return ""
    else:
        return str(value)


def prepare_string_number(string):
    """ Change string to int and empty string to None

    :param string: Text string
    :type string: str
    :return: str or None if the string is empty
    """

    if string == "":
        return None
    else:
        return int(string)


def prepare_textedit(textedit):
    """ Prepare a Textedit content for the database

    :param textedit: Textedit
    :type textedit: Textedit
    :return: HTML str or None if the textedit is empty
    """
    if not textedit.toPlainText() == "":
        return textedit.toHtml()
    else:
        return None


"""
UUID format
"""


def uuid_bytes(value):
    """ Convert an UUID string to bytes

    :param value: UUID string to convert to bytes
    :type value: str or UUID
    :return: bytes
    """
    if type(value) == str:
        return uuid.UUID(value).bytes
    else:
        return value.bytes


def uuid_string(value):
    """ Convert an UUID bytes to string

    :param value: UUID bytes to convert to string
    :type value: bytes
    :return: UUID string
    """
    return str(uuid.UUID(bytes=value))


"""
Encoding
"""


def encode(html):
    """ Encode data to binary

    :param html: HTLM string to encode to binary
    :type html: str
    :returns: Encoded HTML string
    """
    return html.encode()


def decode(html):
    """ Decode data to string

    :param html: HTLM binary to decode
    :type html: bytes
    :returns: HTML string
    """
    return html.decode()
