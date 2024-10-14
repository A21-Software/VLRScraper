from __future__ import annotations

from enum import IntEnum
from typing import Optional, TYPE_CHECKING, List

import vlrscraper.constants as const
from vlrscraper.resource import Resource
from vlrscraper.logger import get_logger
from vlrscraper.scraping import XpathParser
from vlrscraper.utils import parse_first_last_name, get_url_segment

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
        self.__name = tuple(x for x in (forename, surname) if x is not None) or None
        self.__image_src = image
        self.__status = status

    def __eq__(self, other: object) -> bool:
        _logger.warning(
            "Avoid using inbuilt equality for Players. See Player.is_same_player()"
        )
        return object.__eq__(self, other)

    def __repr__(self) -> str:
        return (
            f"Player({self.get_id()}"
            + f", {self.get_display_name()}" * bool(self.get_display_name())
            + f", {self.get_name()}" * bool(self.get_name())
            + f", {self.get_image()}" * bool(self.get_image())
            + f", {0 if (t := self.get_current_team()) is None else t.get_name()}"
            * bool(t)
            + f", {0 if (s := self.get_status()) is None else s.name}"
            * bool(self.get_status())
            + ")"
        )

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
        surname: Optional[str],
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
        surname: Optional[str],
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

    @staticmethod
    def get_players_from_team_page(parser: XpathParser, team: Team) -> List[Player]:
        player_ids = [
            get_url_segment(str(url), 2, rtype=int)
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
        player_tags = [
            parser.get_text(
                f"//a[contains(@href, '{p.lower()}')]//div[contains(@class, 'wf-tag')]"
            )
            for p in player_aliases
        ]
        return [
            Player.from_team_page(
                pid,
                player_aliases[i],
                player_fullnames[i][0],
                player_fullnames[i][1],
                team,
                image=player_images[i],
                status=PlayerStatus.INACTIVE
                if player_tags[i] == "Inactive"
                else PlayerStatus.ACTIVE,
            )
            for i, pid in enumerate(player_ids)
        ]
