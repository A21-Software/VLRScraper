"""This module contains general utility functions that help with scraping websites when fetching data for the
API.

Implements:
    - `get_url_segment`
    - `epoch_from_timestamp`
"""

from datetime import datetime


def get_url_segment(url: str, index: int, rtype: type = str):
    """Isolate the segment of the given url at the index supplied\n
    The `rtype` parameter can be specified to automatically cast the return value,
    if you are trying to extract an integer ID for example

    Args:
        url (str): The url to get the segment from
        index (int): the index of the segment
        rtype (type, optional): The type to cast the segment to before returning. Defaults to str.

    Returns:
        rtype: The segment of the URL
    """
    return rtype(url.split("/")[index].strip())


def epoch_from_timestamp(ts: str, fmt: str) -> float:
    """Converts a given timestamp to seconds from the epoch, given the format of the timestamp

    Args:
        ts (str): The timestamp to convert
        fmt (str): The format of the timestamp to convert to

    Returns:
        float: The time in seconds since the 1st Jan 1970
    """
    return datetime.strptime(ts, fmt).timestamp()
