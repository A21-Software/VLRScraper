from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .resource import Resource
from .scraping import XpathParser
from .utils import get_url_segment, parse_first_last_name
from vlrscraper import constants as const

if TYPE_CHECKING:
    from vlrscraper.player import Player


class Team:
    resource = Resource("https://vlr.gg/team/<res_id>")

    def __init__(
        self, _id: int, name: str, tag: str, logo: str = "", roster: list[Player] = []
    ) -> None:
        self.__id = _id
        self.__name = name
        self.__tag = tag
        self.__logo = logo
        self.__roster = roster

    def __eq__(self, other: Team) -> bool:
        return (
            isinstance(other, Team)
            and self.get_id() == other.get_id()
            and self.get_name() == other.get_name()
            and self.get_tag() == other.get_tag()
            and self.get_logo() == other.get_logo()
            and self.get_roster() == other.get_roster()
        )

    def __repr__(self) -> str:
        return f"{self.get_name()} / {self.get_tag()}, [{self.get_logo()}]"

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_tag(self) -> str:
        return self.__tag

    def get_logo(self) -> str:
        return self.__logo

    def get_roster(self) -> list[Player]:
        return self.__roster

    @staticmethod
    def get_team(_id: int) -> Optional[Team]:
        data = Team.resource.get_data(_id)
        if not data["success"]:
            return None

        parser = XpathParser(data["data"])

        player_ids = [
            get_url_segment(url, 2, rtype=int)
            for url in parser.get_elements(const.TEAM_ROSTER_ITEMS, "href")
        ]
        player_aliases = parser.get_text_many(const.TEAM_ROSTER_ITEM_ALIAS)
        player_fullnames = [
            parse_first_last_name(name)
            for name in parser.get_text_many(const.TEAM_ROSTER_ITEM_FULLNAME)
        ]
        player_images = [
            f"https:{img}"
            for img in parser.get_elements(const.TEAM_ROSTER_ITEM_IMAGE, "src")
        ]

        from vlrscraper.player import Player

        return Team(
            _id,
            parser.get_text(const.TEAM_DISPLAY_NAME),
            parser.get_text(const.TEAM_TAG),
            f"https:{parser.get_img(const.TEAM_IMG)}",
            [
                Player(
                    pid,
                    player_aliases[i],
                    _id,
                    *player_fullnames[i],
                    image=player_images[i],
                )
                for i, pid in enumerate(player_ids)
            ],
        )
