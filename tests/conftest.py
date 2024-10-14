import json
import pytest
import requests

from typing import Callable, Optional
from vlrscraper.logger import get_logger

regression_json: dict


def pytest_sessionstart(session):
    global regression_json
    with open("regressions.json", "r+") as f:
        regression_json = json.load(f)["regressions"]


def pytest_sessionfinish(session, exitstatus):
    global regression_json
    with open("regressions.json", "w+") as f:
        json.dump({"regressions": regression_json}, f)


def get_regression(url: str) -> Optional[dict]:
    global regression_json
    return regression_json.get(url, None)


def save_regression(url, response) -> None:
    global regression_json
    regression_json.update(
        {
            url: {
                "status-code": response.status_code,
                "content": response.content.decode("utf-8"),
            }
        }
    )


def requests_get_patch(original_get: Callable):
    def patch(url):
        result = original_get(url)
        if (regression := get_regression(url)) is not None:
            get_logger().debug(f"Using regression stored for {url}")
            result.status_code = regression["status-code"]
            result._content = regression["content"].encode("utf-8")
        else:
            save_regression(url, result)
        return result

    return patch


@pytest.fixture
def requests_regression():
    old_get = requests.get
    requests.get = requests_get_patch(old_get)
    yield
    requests.get = old_get
