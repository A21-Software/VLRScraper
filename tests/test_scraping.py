# type: ignore
import pytest

import requests

from vlrscraper.scraping import xpath, XpathParser, join


def test_xpath():
    assert (
        xpath("div", class_="test-class", id_="test-id")
        == "//div[contains(@class, 'test-class') and contains(@id, 'test-id')]"
    )
    assert (
        xpath("span", aria_label="test-label")
        == "//span[contains(@aria_label, 'test-label')]"
    )
    assert (
        xpath("span", aria__label="test-label")
        == "//span[contains(@aria-label, 'test-label')]"
    )
    assert (
        xpath("span", aria__label="test-label", class_="test")
        == "//span[contains(@class, 'test') and contains(@aria-label, 'test-label')]"
    )

    assert (
        xpath("div", root=xpath("span", aria__label="label"), class_="test-class")
        == "//span[contains(@aria-label, 'label')]//div[contains(@class, 'test-class')]"
    )


def test_xpathJoin():
    assert (
        join("div[0]", "div[1]", xpath("img", src="rigger.jpg"))
        == "//div[0]//div[1]//img[contains(@src, 'rigger.jpg')]"
    )


# TODO: Add regression testing for this :D
def test_xpathParser():
    data = requests.get("https://www.vlr.gg/player/29873/benjyfishy")
    parser = XpathParser(data.content)
    assert parser.get_text(xpath("h1", class_="wf-title")) == "benjyfishy"
    assert (
        parser.get_element(xpath("h1", class_="wf-title")).text.strip() == "benjyfishy"
    )

    assert len(parser.get_elements(xpath("a", class_="wf-card"))) == 5
    assert (
        parser.get_href("//a[contains(@class, 'wf-nav-item')][2]")
        == "/player/matches/29873/benjyfishy"
    )
    assert (
        parser.get_img(xpath("img", root=xpath("div", class_="mod-player")))
        == "//owcdn.net/img/665b77ca4bc4d.png"
    )

    assert parser.get_text(xpath("img", root=xpath("div", class_="mod-player"))) == ""

    with pytest.raises(TypeError):
        XpathParser("skibidi sigma")
