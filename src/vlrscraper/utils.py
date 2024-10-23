"""This module contains general utility functions that help with scraping websites when fetching data for the
API.
"""

import time

from threading import Thread
from datetime import datetime
from typing import TypeVar, Type, Optional, Tuple, List, Any

from collections.abc import Callable

from vlrscraper.logger import get_logger

_logger = get_logger()


def parse_first_last_name(name: str) -> Tuple[str, Optional[str]]:
    """Parse the first and last name of a player, given the string scraped from their VLR.gg page

    :param name: The player's full name
    :type name: str

    :return: A tuple containing the first name, and either the second name or `None` if no second name could be found.
    :rtype: Tuple[str, Optional[str]]
    """
    names = name.split(" ")
    # Get rid of non-ascii names (ie korean names)
    if names[-1].startswith("("):
        names.pop(-1)

    # Only one name (Weird ?)
    if len(names) == 1:
        return (names[0], None)
    return names[0], names[-1]


T = TypeVar("T", int, float, str)


def parse_stat(stat: Optional[str], rtype: Type) -> Optional[T]:
    """Parse a statistic string from a player's match performance tab on VLR.gg

    :param stat: The string data scraped from the match page
    :type stat: Optional[str]

    :param rtype: The type to cast the stat to
    :type rtype: :class:`typing.Type`

    :return: The value of the stat, default None
    :rtype: T
    """
    if stat == "\xa0" or stat is None:
        return None
    return rtype(stat.replace("%", "").strip())


def get_url_segment(url: str, index: int, rtype: type = str) -> T:
    """Isolate the segment of the given url at the index supplied\n
    The `rtype` parameter can be specified to automatically cast the return value,
    if you are trying to extract an integer ID for example

    :param url: The url to get the segment from
    :type url: str

    :param index: The index of the segment
    :type index: int

    :param rtype: The type to cast the segment to before returning, defaults to None
    :type rtype: type

    :return: The segment of the URL
    :rtype: T
    """
    return rtype(url.split("/")[index].strip())


def epoch_from_timestamp(ts: str, fmt: str) -> float:
    """Convert a given timestamp to seconds from the epoch, given the format of the timestamp

    :param ts: The timestamp to convert
    :type ts: str

    :param fmt: The format of the timestamp to convert
    :type fmt: str

    :return: The time in seconds since the 1st Jan 1970
    :rtype: float
    """
    return datetime.strptime(ts, fmt).timestamp()


def previous_epoch(
    years: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> float:
    """Get the epoch y years, d days, h hours, m minutes and s seconds in the past

    :param year: The amount of years to go back, by default 0
    :type year: int, optional

    :param days: The amount of days to go back, by default 0
    :type days: int, optional

    :param hours: The amount of hours to go back, by default 0
    :type hours: int, optional

    :param minutes: The amount of minutes to go back, by default 0
    :type minutes: int, optional

    :return: The epoch requested
    :rtype: float
    """
    total_loss = (
        ((years * 365.0 + days) * 24.0 + hours) * 60 + minutes
    ) * 60.0 + seconds
    return time.time() - total_loss


def test_performance(func: Callable) -> None:
    """Decorator to test the performance of a function by timing it and logging the result to the
    logger's info stream

    :param func: The function to decorate
    :type func: :class:`collections.abc.Callable`
    """

    def inner(*args, **kwargs):
        timeStart = time.perf_counter()
        return_val = func(*args, **kwargs)
        _logger.info(
            f"Function {func.__name__} took {time.perf_counter() - timeStart} seconds to run."
        )
        return return_val

    return inner


def partion(lst: List[Any], n: int) -> List[List[Any]]:
    """Partition a list into n even chunks. If the list does not divide evenly into n chunks then
    the amount of items in each sub-array will differ by most 1.

    :param lst: The list to partition
    :type lst: List[:class:`typing.Any`]

    :param n: The number of partitions to create
    :type n: int

    :return: The list of partitioned data
    :rtype: List[List[:class:`typing.Any`]]
    """
    return [lst[i::n] for i in range(n)]


def thread_over_data(data: List[Any], data_cb: Callable, threads: int = 4) -> None:
    """Map a function in parallel over some supplied data

    :param data: The data to map the function to
    :type data: :class:`typing.Any`

    :param data_cb: The function to map the data to
    :type data_cb: :class:`collections.abc.Callable`

    :param threads: The number of threads to use, by default 4
    :type threads: int
    """
    # deal with len(data) < threads
    num_threads = min(len(data), threads)

    # partion data
    split_data = partion(data, num_threads)

    def do_thread(data: List[Any]) -> None:
        for i in data:
            data_cb(i)

    thread_pool = [
        Thread(target=do_thread, args=(split_data[i],)) for i in range(num_threads)
    ]

    for thread in thread_pool:
        thread.start()

    for thread in thread_pool:
        thread.join()


def resolve_vlr_image(url: str) -> str:
    """Get the full image URL from a partial URL scraped from VLR.gg

    :param url: The URL of the image to resolve
    :type url: str

    :return: The absolute URL of the image
    :rtype: str
    """
    return "https:" + url if url.startswith("//") else f"https://vlr.gg{url}"
