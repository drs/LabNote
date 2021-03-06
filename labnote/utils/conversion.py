""" This module contains custom type conversion functions """

# Python import
import uuid


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


def encode_experiment(html):
    """ Encode experiment data to binary

    :param html: HTLM string to encode to binary
    :type html: str
    :returns: Encoded HTML string
    """
    return html.encode()


def decode_experiment(html):
    """ Decole experiment data to string

    :param html: HTLM binary to decode
    :type html: bytes
    :returns: HTML string
    """
    return html.decode()