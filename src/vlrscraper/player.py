from __future__ import annotations
from typing import Optional

from .resource import Resource


class Player:
    resource = Resource("https://www.vlr.gg/player/<res_id>")

    def __init__(
        self,
        _id: int,
        name: str,
        current_team: int,
        forename: str = "",
        surname: str = "",
        image: str = "",
    ) -> None:
        self.__id = _id
        self.__displayname = name
        self.__current_team = current_team
        self.__name = (forename, surname)
        self.__image_src = image

    def __eq__(self, other: Player) -> bool:
        return (
            isinstance(other, Player)
            and self.__id == other.get_id()
            and self.__displayname == other.get_display_name()
            and self.__current_team == other.get_current_team()
            and self.__name == other.get_name()
            and self.__image_src == other.get_image()
        )

    def __repr__(self) -> str:
        return f"{self.__displayname} ({' '.join(self.__name)})"

    def get_id(self) -> int:
        return self.__id

    def get_display_name(self) -> str:
        return self.__displayname

    def get_current_team(self) -> int:
        return self.__current_team

    def get_name(self) -> str:
        return ' '.join(self.__name)

    def get_image(self) -> str:
        return self.__image_src

    @staticmethod
    def get_player(_id: int) -> Optional[Player]:
        data = Player.resource.get_data(_id)
        if not data["success"]:
            return None

