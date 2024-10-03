from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from enum import IntEnum

import vlrscraper.constants as const
from vlrscraper.logger import get_logger
from vlrscraper.resource import Resource
from vlrscraper.scraping import XpathParser, join
from vlrscraper.utils import get_url_segment, parse_first_last_name

if TYPE_CHECKING:
    from vlrscraper.team import Team


class PlayerStatus(IntEnum):
    INACTIVE = 1
    ACTIVE = 2

    def __repr__(self) -> str:
        return self.name


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
        return self == other

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

        player_name = parse_first_last_name(parser.get_text(const.PLAYER_FULLNAME))

        from vlrscraper.team import Team

        team_id = get_url_segment(
            parser.get_href(const.PLAYER_CURRENT_TEAM), 2, rtype=int
        )

        imgpath = join(const.PLAYER_CURRENT_TEAM, "img")[2:]
        namepath = join(const.PLAYER_CURRENT_TEAM, "div[2]", "div[1]")[2:]

        team_image = f"https:{parser.get_img(imgpath)}"
        team_name = parser.get_text(namepath)

        return Player.from_player_page(
            _id,
            parser.get_text(const.PLAYER_DISPLAYNAME),
            player_name[0],
            player_name[-1],
            Team.from_player_page(team_id, team_name, team_image),
            f"https:{parser.get_img(const.PLAYER_IMAGE_SRC)}",
            PlayerStatus.ACTIVE
            if len(parser.get_elements(const.PLAYER_INACTIVE_CHECK)) <= 2
            else PlayerStatus.INACTIVE,
        )
