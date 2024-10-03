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
        self,
        _id: int,
        name: Optional[str],
        tag: Optional[str],
        logo: Optional[str],
        roster: Optional[list[Player]],
    ) -> None:
        self.__id = _id
        self.__name = name
        self.__tag = tag
        self.__logo = logo
        self.__roster = roster

        self.__fully_scraped = True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Team)
            and self.get_id() == other.get_id()
            and self.get_name() == other.get_name()
            and self.get_tag() == other.get_tag()
            and self.get_logo() == other.get_logo()
        )

    def __repr__(self) -> str:
        return f"{self.get_name()} / {self.get_tag()}, [{self.get_logo()}]"

    def get_id(self) -> int:
        """Get the vlr ID of this team

        Returns
        -------
        int
            vlr ID
        """
        return self.__id

    def get_name(self) -> str:
        """Get the name of this team

        Returns
        -------
        str
            The name of the team
        """
        return self.__name

    def get_tag(self) -> str:
        """Get the 1-3 letter team tag of this team

        Returns
        -------
        str
            The team tag
        """
        return self.__tag

    def get_logo(self) -> str:
        """Get the URL of this team's logo

        Returns
        -------
        str
            The team logo
        """
        return self.__logo

    def get_roster(self) -> list[Player]:
        """Get the list of players / staff for this team

        Returns
        -------
        list[Player]
            The team roster
        """
        return self.__roster

    def set_roster(self, roster: list[Player]) -> None:
        self.__roster = roster

    def set_fully_scraped(self, scraped: bool) -> None:
        self.__fully_scraped = scraped

    def get_fully_scraped(self) -> bool:
        return self.__fully_scraped

    @staticmethod
    def from_team_page(
        _id: int, name: str, tag: str, logo: str, roster: list[Player]
    ) -> Team:
        """Construct a Team object from the data available on the team's page

        Parameters
        ----------
        _id : int
            The vlr id of the team
        name : str
            The full name of the team
        tag : str
            The 1-3 letter tag of the team
        logo : str
            The url of the team's logo
        roster : list[Player]
            List of players and staff on the team

        Returns
        -------
        Team
            The team object created using the given values
        """
        team = Team(_id, name, tag, logo, roster)
        team.set_fully_scraped(True)
        return team

    @staticmethod
    def from_player_page(_id: int, name: str, logo: str) -> Team:
        """Construct a Team object from the data available on a player's page

        Data loaded from the player page: `id`, `name` and `logo`\n

        Parameters
        ----------
        _id : int
            The vlr id of the team
        name : str
            The full name of the team
        logo : str
            The url of the team's logo

        Returns
        -------
        Team
            The team object created using the given values
        """
        team = Team(_id, name=name, tag=None, logo=logo, roster=None)
        team.set_fully_scraped(False)
        return team

    @staticmethod
    def from_match_page(
        _id: int, name: str, tag: str, logo: str, roster: list[Player]
    ) -> Team:
        team = Team(_id, name, tag, logo, roster)
        team.set_fully_scraped(True)
        return team

    @staticmethod
    def get_team(_id: int) -> Optional[Team]:
        """Fetch team data from vlr.gg given the ID of the team

        Parameters
        ----------
        _id : int
            The ID of the team on vlr.gg

        Returns
        -------
        Optional[Team]
            The team data if the ID given was valid, otherwise `None`
        """
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
        player_tags = [
            parser.get_text(
                f"//a[contains(@href, '{p.lower()}')]//div[contains(@class, 'wf-tag')]"
            )
            for p in player_aliases
        ]

        from vlrscraper.player import Player, PlayerStatus

        team = Team.from_team_page(
            _id,
            parser.get_text(const.TEAM_DISPLAY_NAME),
            parser.get_text(const.TEAM_TAG),
            f"https:{parser.get_img(const.TEAM_IMG)}",
            [],
        )

        team.set_roster(
            list(
                [
                    Player.from_team_page(
                        pid,
                        player_aliases[i],
                        *player_fullnames[i],
                        team,
                        image=player_images[i],
                        status=PlayerStatus.INACTIVE
                        if player_tags[i] == "Inactive"
                        else PlayerStatus.ACTIVE,
                    )
                    for i, pid in enumerate(player_ids)
                ]
            ),
        )
        return team
