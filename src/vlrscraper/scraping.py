"""This module implements classes and functions that help with scraping data by XPATHs

Implements:
    - `XpathParser`, a class that can be used to scrape sites by xpath strings
    - `xpath`, a function that generates xpath strings based on the arguments passed
"""

from typing import Optional, List, Union

from lxml import html
from lxml.html import HtmlMixin, HtmlElement
from lxml.etree import _Element

from vlrscraper.logger import get_logger

_logger = get_logger()


class XpathParser:
    """Implements easier methods of parsing XPATH
    directly from data returned from a `requests.get()` call
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

        Args:
            xpath (str): the XPATH to find the link at.

        Returns:
            Optional[str]: the data contained in the `href` tag of the `HtmlElement` at the XPATH, or None if the href tag cannot be located.
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
    Performs a similar function to os.path.join()

    Args:
        *xpath (list[str]): The xpaths or elements to combine

    Returns:
        str: _description_
    """
    return "//" + "//".join(map(lambda f: f[2:] if f.startswith("//") else f, xpath))
