"""This module implements classes and functions that help with scraping data by XPATHs

Implements:
    - `XpathParser`, a class that can be used to scrape sites by xpath strings
    - `xpath`, a function that generates xpath strings based on the arguments passed
"""

import time
import requests

from threading import Thread
from typing import Optional, List, Union, Tuple

from lxml import html
from lxml.html import HtmlMixin, HtmlElement
from lxml.etree import _Element

from vlrscraper.resources import Match
from vlrscraper.logger import get_logger
from vlrscraper.utils import thread_over_data

_logger = get_logger()


class XpathParser:
    """Implements easier methods of parsing XPATH
    directly from data returned from a `requests.get()` call

    :param data: The response data of the reqest to parse
    :type data: bytes
    """

    def __init__(self, data: bytes) -> None:
        """Creates a parser that is capable of taking XPATH's and returning desired objects

        Args:
            url (str): The url of the website to parse
        """
        if isinstance(data, bytes):
            self.content = html.fromstring(data)
        else:
            raise TypeError("Data must be either string or HtmlElement")

    def get_element(self, xpath: str) -> Optional[HtmlElement]:
        """Gets a single HTML element from an XPATH string

        Args:
            xpath (str): The XPATH to the element

        Returns:
            html.HtmlElement: the HtmlElement at the desired XPATH
        """
        elem = self.content.xpath(xpath)
        if isinstance(elem, list):
            return elem[0] if elem else None
        return None

    def get_elements(
        self, xpath: str, attr: str = ""
    ) -> Union[List[HtmlElement], List[str]]:
        """Gets a list of htmlElements that match a given XPATH

        TODO: Do we want this to return null values for failed GETS or do we want this to return only the successful
        elements

        Args:
            xpath (str): The XPATH to match the elements to
            attr (str): The attribute to get from each element (or '')

        Returns:
            List[str | html.HtmlElement]: The list of elements that match the given XPATH
        """

        elements = self.content.xpath(xpath)

        if not isinstance(elements, list):
            return []

        return (
            [
                str(elem.get(attr, None))
                for elem in elements
                if isinstance(elem, _Element)
            ]
            if attr
            else elements
        )

    def get_img(self, xpath: str) -> str:
        """Gets an image src from a given XPATH string

        Args:
            xpath (str): the XPATH to find the image at.

        Returns:
            Optional[str]: the data contained in the `src` tag of the `HtmlElement` at the XPATH, or None if the src tag cannot be located.
        """
        if (element := self.get_element(xpath)) is None:
            return ""
        return element.get("src", "").strip()

    def get_href(self, xpath: str) -> str:
        """Gets an link href from a given XPATH string

        :param xpath: The XPATH to find the link at
        :type xpath: str

        :return: The data contained in the href tag of the :class:`lxml.html.HtmlElement` at the XPATH, or "" if the href tag cannot be located
        :rtype: str
        """
        if (element := self.get_element(xpath)) is None:
            return ""
        return element.get("href", "").strip()

    def get_text(self, xpath: str) -> str:
        """Gets the inner text of the given XPATH

        Args:
            xpath (str): The XPATH to find the text container at

        Returns:
            Optional[str]: The inner text of the element, or None if no element or text could be found
        """

        elem = self.get_element(xpath)

        # There is no text so return None
        if elem is None or (txt := elem.text) is None:
            return ""

        return txt.replace("\n", "").replace("\t", "").strip()

    def get_text_from_element(self, elem: HtmlMixin) -> str:
        return str(elem.text_content()).replace("\t", "").replace("\n", "").strip()

    def get_text_many(self, xpath: str) -> List[str]:
        elems = self.get_elements(xpath)

        return [
            self.get_text_from_element(elem)
            for elem in elems
            if isinstance(elem, HtmlMixin)
        ]


def xpath(elem: str, root: str = "", **kwargs) -> str:
    """Create an XPATH string that selects the element passed into the `elem` parameter which matches the htmlelement
    attributes specified using the keyword arguments.

    Since `class` and `id` are restriced keywords in python, if you want to get an element by either of these, use
    `class_=<>` and `id_=<>` instead, and the function will automatically remove the "_"

    Args:
        elem (str): The element to select. For example, `div`, `class`, `a`
        root (str, optional): An optional XPATH that is the root node of this XPATH. Defaults to ''.

    Returns:
        str: The XPATH created
    """

    # Replace class_ and id_ filters with corresponding html tags
    filters = {
        "class": kwargs.pop("class_", None),
        "id": kwargs.pop("id_", None),
        **kwargs,
    }
    kwgs = [kwg for kwg in filters if "__" in kwg]
    for kwg in kwgs:
        filters.update({kwg.replace("__", "-"): filters.pop(kwg)})

    # Worst f string ever :D
    return f"{root}//{elem}[{' and '.join(f'''contains(@{arg}, '{filters[arg]}')''' for arg in [k for k, v in filters.items() if v])}]".replace(
        "[]", ""
    )


def join(*xpath: str) -> str:
    """Create an xpath that is the combination of the xpaths provided
    Performs a similar function to `os.path.join()`

    :param \*xpath: The xpaths or elements to combine
    :type xpath: List[str]

    :return: The result of a join across all given xpaths
    :rtype: str
    """
    return "//" + "//".join(map(lambda f: f[2:] if f.startswith("//") else f, xpath))


class ThreadedMatchScraper:
    def __init__(self, ids: list[int]) -> None:
        self.__ids: List[int] = ids
        self.__responses: List[Tuple[int, bytes]] = []
        self.__data: List[Match] = []
        self.__scraping = False

    def fetch_single_url(self, _id: int) -> None:
        response = requests.get(f"https://vlr.gg/{_id}")
        if response.status_code == 200:
            self.__responses.append((_id, response.content))
        else:
            _logger.warning(
                f"Could not fetch data for match {_id}: {response.status_code}"
            )

    def fetch_urls(self) -> None:
        _logger.info(f"Began fetch URL thread for {self}")
        """ for _id in self.__ids:
            response = requests.get(f"https://vlr.gg/{_id}")
            if response.status_code == 200:
                self.__responses.append((_id, response.content))
            else:
                _logger.warning(f"Could not fetch data for match {_id}: {response.status_code}") """
        thread_over_data(self.__ids, self.fetch_single_url, 2)
        self.__scraping = False

    def parse_data(self) -> None:
        _logger.info(f"Begain data parsing thread for {self}")
        from vlrscraper.controllers import MatchController

        while self.__scraping or self.__responses:
            if not self.__responses:
                time.sleep(0.2)
                continue
            _id, data = self.__responses.pop(0)
            self.__data.append(MatchController.parse_match(_id, data))

    def run(self) -> list[Match]:
        fetch_thread = Thread(target=self.fetch_urls)
        parse_thread = Thread(target=self.parse_data)

        self.__scraping = True

        fetch_thread.start()
        parse_thread.start()
        parse_thread.join()

        return sorted(self.__data, key=lambda m: m.get_date(), reverse=True)
