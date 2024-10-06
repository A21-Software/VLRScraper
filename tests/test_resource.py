# type: ignore
import pytest

from vlrscraper.resource import Resource, ResourceResponse


def test_init():
    res = Resource("https://www.vlr.gg/player/<res_id>")
    assert res.get_base_url() == "https://www.vlr.gg/player/<res_id>"

    with pytest.raises(TypeError):
        res = Resource(10000)

    with pytest.raises(ValueError):
        res = Resource("https://www.vlr.gg/player/id")


def test_get_url():
    res = Resource("https://www.vlr.gg/player/<res_id>")
    assert res.get_url(1) == "https://www.vlr.gg/player/1"
    assert res.get_url(1.0) == ""


def test_get_data():
    res = Resource("https://www.vlr.gg/player/<res_id>")
    assert res.get_data(1.0) == ResourceResponse.id_invalid(1.0)
    assert res.get_data(-1000) == ResourceResponse.request_refused(
        "https://www.vlr.gg/player/-1000", 404
    )

    assert res.get_data(4000)["success"] is True
