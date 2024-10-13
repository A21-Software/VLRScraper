"""This module contains general utility functions that help with scraping websites when fetching data for the
API.

Implements:
    - `get_url_segment`
    - `epoch_from_timestamp`
"""

import time

from threading import Thread
from datetime import datetime
from typing import TypeVar, Type, Optional, Tuple, Callable, List, Any

from vlrscraper.logger import get_logger

_logger = get_logger()


def parse_first_last_name(name: str) -> Tuple[str, Optional[str]]:
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
    if stat == "\xa0" or stat is None:
        return None
    return rtype(stat.replace("%", "").strip())


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


def previous_epoch(
    years: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> float:
    total_loss = (
        ((years * 365.0 + days) * 24.0 + hours) * 60 + minutes
    ) * 60.0 + seconds
    return time.time() - total_loss


def test_performance(func: Callable):
    def inner(*args, **kwargs):
        timeStart = time.perf_counter()
        return_val = func(*args, **kwargs)
        _logger.info(
            f"Function {func.__name__} took {time.perf_counter() - timeStart} seconds to run."
        )
        return return_val

    return inner


def partion(lst: List[Any], n: int) -> List[List[Any]]:
    return [lst[i::n] for i in range(n)]


def thread_over_data(data: List[Any], data_cb: Callable, threads: int = 4) -> None:
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
