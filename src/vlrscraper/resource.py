from typing import Any

import requests


class ResourceResponse:
    @staticmethod
    def id_invalid(_id: Any) -> dict:
        return {"success": False, "error": f"Invalid id given: {_id}"}

    @staticmethod
    def request_refused(url: str, code: int) -> dict:
        return {
            "success": False,
            "error": f"Invalid status code {code} recieved when fetching data from {url}",
        }

    @staticmethod
    def success(data) -> dict:
        return {"success": True, "data": data}


class Resource:
    def __init__(self, url: str) -> None:
        if not isinstance(url, str):
            raise TypeError("Resource URLs must be strings.")
        if "<res_id>" not in url:
            raise ValueError("Resource URLs must contain some reference to <res_id>.")
        self.__url = url

    def get_base_url(self) -> str:
        return self.__url

    def get_url(self, _id: int) -> str:
        """Get the URL that would be used to fetch data for the given resource ID

        Args:
            _id (int): The resource (vlr) ID of the resource being requested

        Returns:
            str: The url that the resource can be found at
        """
        if not isinstance(_id, int):
            return ""
        return self.__url.replace("<res_id>", str(_id))

    def get_data(self, _id: int, json: bool = False) -> dict:
        if not (url := self.get_url(_id)):
            return ResourceResponse.id_invalid(_id)

        response = requests.get(url)
        return (
            ResourceResponse.success(response.json() if json else response.content)
            if response.status_code == 200
            else ResourceResponse.request_refused(url, response.status_code)
        )
