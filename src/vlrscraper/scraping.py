"""This module implements classes and functions that help with scraping data by XPATHs

Implements:
    - `XpathParser`, a class that can be used to scrape sites by xpath strings
    - `xpath`, a function that generates xpath strings based on the arguments passed
"""
from typing import Optional

from lxml import html


class XpathParser:
    """Implements easier methods of parsing XPATH
    directly from data returned from a `requests.get()` call
    """

    def __init__(self, data: str) -> None:
        """Creates a parser that is capable of taking XPATH's and returning desired objects

        Args:
            url (str): The url of the website to parse
        """
        self.content = html.fromstring(data)

    def get_element(self, xpath: str) -> Optional[html.HtmlElement]:
        """Gets a single HTML element from an XPATH string

        Args:
            xpath (str): The XPATH to the element

        Returns:
            html.HtmlElement: the HtmlElement at the desired XPATH
        """
        elem = self.content.xpath(xpath)
        return elem[0] if elem else None

    def get_elements(self, xpath: str, attr: str = "") -> list[html.HtmlElement]:
        """Gets a list of htmlElements that match a given XPATH

        TODO: Do we want this to return null values for failed GETS or do we want this to return only the successful
        elements

        Args:
            xpath (str): The XPATH to match the elements to
            attr (str): The attribute to get from each element (or '')

        Returns:
            list[str | html.HtmlElement]: The list of elements that match the given XPATH
        """
        return (
            [elem.get(attr, None) for elem in self.content.xpath(xpath)]
            if attr
            else self.content.xpath(xpath)
        )

    def get_img(self, xpath: str) -> Optional[str]:
        """Gets an image src from a given XPATH string

        Args:
            xpath (str): the XPATH to find the image at.

        Returns:
            Optional[str]: the data contained in the `src` tag of the `HtmlElement` at the XPATH, or None if the src tag cannot be located.
        """
        return self.get_element(xpath).get("src", "").strip() or None

    def get_href(self, xpath: str) -> Optional[str]:
        """Gets an link href from a given XPATH string

        Args:
            xpath (str): the XPATH to find the link at.

        Returns:
            Optional[str]: the data contained in the `href` tag of the `HtmlElement` at the XPATH, or None if the href tag cannot be located.
        """
        return self.get_element(xpath).get("href", "").strip() or None

    def get_text(self, xpath: str) -> Optional[str]:
        """Gets the inner text of the given XPATH

        Args:
            xpath (str): The XPATH to find the text container at

        Returns:
            Optional[str]: The inner text of the element, or None if no element or text could be found
        """

        elem = self.get_element(xpath)

        # There is no text so return None
        if elem == {} or not elem.text:
            return None

        return elem.text.strip()


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


def join(*xpath: list[str]) -> str:
    """Create an xpath that is the combination of the xpaths provided
    Performs a similar function to os.path.join()

    Args:
        *xpath (list[str]): The xpaths or elements to combine

    Returns:
        str: _description_
    """
    return "//" + "//".join(map(lambda f: f[2:] if f.startswith("//") else f, xpath))
