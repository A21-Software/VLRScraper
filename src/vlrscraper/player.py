from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from enum import IntEnum

import vlrscraper.constants as const
from vlrscraper.resource import Resource
from vlrscraper.logger import get_logger
from vlrscraper.scraping import XpathParser
from vlrscraper.utils import parse_first_last_name

if TYPE_CHECKING:
    from vlrscraper.team import Team


class PlayerStatus(IntEnum):
    INACTIVE = 1
    ACTIVE = 2


_logger = get_logger()


class Player:
    resource = Resource("https://www.vlr.gg/player/<res_id>")

    def __init__(
        self,
        _id: int,
        name: Optional[str],
        current_team: Optional[Team],
        forename: Optional[str],
        surname: Optional[str],
        image: Optional[str],
        status: Optional[PlayerStatus],
    ) -> None:
        if not isinstance(_id, int) or _id <= 0:
            raise ValueError("Player ID must be an integer {0 < ID}")

        self.__id = _id
        self.__displayname = name
        self.__current_team = current_team
        self.__name = (
            tuple(filter(lambda x: x is not None, (forename, surname))) or None
        )
        self.__image_src = image
        self.__status = status

    def __eq__(self, other: object) -> bool:
        _logger.warning(
            "Avoid using inbuilt equality for Players. See Player.is_same_player()"
        )
        return object.__eq__(self, other)

    def __repr__(self) -> str:
        return f"Player({self.get_id()}, {self.get_display_name()}, {self.get_name()}, {self.get_image()}, {self.get_current_team()}, {self.get_status().name if self.get_status() else None})"

    def get_id(self) -> int:
        return self.__id

    def get_display_name(self) -> Optional[str]:
        return self.__displayname

    def get_current_team(self) -> Optional[Team]:
        return self.__current_team

    def get_name(self) -> Optional[str]:
        return " ".join(self.__name) if self.__name is not None else None

    def get_image(self) -> Optional[str]:
        return self.__image_src

    def get_status(self) -> Optional[PlayerStatus]:
        return self.__status

    def is_same_player(self, other: object) -> bool:
        return (
            isinstance(other, Player)
            and self.get_id() == other.get_id()
            and self.get_display_name() == other.get_display_name()
            and self.get_name() == other.get_name()
            and self.get_image() == other.get_image()
        )

    @staticmethod
    def from_player_page(
        _id: int,
        display_name: str,
        forename: str,
        surname: str,
        current_team: Team,
        image: str,
        status: PlayerStatus,
    ) -> Player:
        return Player(_id, display_name, current_team, forename, surname, image, status)

    @staticmethod
    def from_team_page(
        _id: int,
        display_name: str,
        forename: str,
        surname: str,
        current_team: Team,
        image: str,
        status: PlayerStatus,
    ) -> Player:
        return Player(_id, display_name, current_team, forename, surname, image, status)

    @staticmethod
    def from_match_page(_id: int, display_name: str) -> Player:
        """_summary_

        Parameters
        ----------
        _id : int
            _description_
        display_name : str
            _description_

        Returns
        -------
        Player
            _description_
        """
        return Player(_id, display_name, None, None, None, None, None)

    @staticmethod
    def get_player(_id: int) -> Optional[Player]:
        data = Player.resource.get_data(_id)
        if not data["success"]:
            return None

        parser = XpathParser(data["data"])

        player_alias = parser.get_text(const.PLAYER_DISPLAYNAME)
        player_image = f"https:{parser.get_img(const.PLAYER_IMAGE_SRC)}"
        player_name = parse_first_last_name(parser.get_text(const.PLAYER_FULLNAME))
        player_status = (
            PlayerStatus.ACTIVE
            if len(parser.get_elements(const.PLAYER_INACTIVE_CHECK)) <= 2
            else PlayerStatus.INACTIVE
        )

        from vlrscraper.team import Team

        return Player.from_player_page(
            _id,
            player_alias,
            player_name[0],
            player_name[-1],
            Team.get_team_from_player_page(parser=parser),
            player_image,
            player_status,
        )
