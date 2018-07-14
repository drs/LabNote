""" This module handle date manipulation """

# Python import
from datetime import datetime
from dateutil import tz


def utc_to_local(date, format='%Y-%m-%d %H:%M:%S'):
    """ Convert an utc date string to a local date sting

    :param date: UTC date
    :type date: str
    :param format: Date formatting
    :type format: str
    :return str: Local date
    """

    utc_tz = tz.tzutc()
    local_tz = tz.tzlocal()

    utc = datetime.strptime(date, format)
    utc = utc.replace(tzinfo=utc_tz)

    local = utc.astimezone(local_tz)

    return datetime.strftime(local, '%Y-%m-%d %H:%M')