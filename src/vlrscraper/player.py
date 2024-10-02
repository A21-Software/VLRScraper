from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from enum import IntEnum

import vlrscraper.constants as const

from vlrscraper.resource import Resource
from vlrscraper.scraping import XpathParser, join
from vlrscraper.utils import get_url_segment, parse_first_last_name

if TYPE_CHECKING:
    from vlrscraper.team import Team


class PlayerStatus(IntEnum):
    INACTIVE = 1
    ACTIVE = 2
    SUB = 3


class Player:
    resource = Resource("https://www.vlr.gg/player/<res_id>")

    def __init__(
        self,
        _id: int,
        name: str,
        current_team: Team,
        forename: str = "",
        surname: str = "",
        image: str = "",
        status: PlayerStatus = PlayerStatus.ACTIVE,
    ) -> None:
        self.__id = _id
        self.__displayname = name
        self.__current_team = current_team
        self.__name = (forename, surname)
        self.__image_src = image
        self.__status = status

    def __eq__(self, other: Player) -> bool:
        return (
            isinstance(other, Player)
            and self.get_id() == other.get_id()
            and self.get_display_name() == other.get_display_name()
            and self.get_current_team() == other.get_current_team()
            and self.get_name() == other.get_name()
            and self.get_image() == other.get_image()
            and self.get_status() == other.get_status()
        )

    def __repr__(self) -> str:
        return f"{self.get_display_name()} ({self.get_name()}) [{self.get_image()}]"

    def get_id(self) -> int:
        return self.__id

    def get_display_name(self) -> str:
        return self.__displayname

    def get_current_team(self) -> int:
        return self.__current_team

    def get_name(self) -> str:
        return " ".join(self.__name)

    def get_image(self) -> str:
        return self.__image_src

    def get_status(self) -> PlayerStatus:
        return self.__status

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

        return Player(
            _id,
            parser.get_text(const.PLAYER_DISPLAYNAME),
            Team(team_id, team_name, "", logo=team_image),
            player_name[0],
            player_name[-1],
            f"https:{parser.get_img(const.PLAYER_IMAGE_SRC)}",
            PlayerStatus.ACTIVE
            if len(parser.get_elements(const.PLAYER_INACTIVE_CHECK)) <= 2
            else PlayerStatus.INACTIVE,
        )
