from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

from vlrscraper.logger import get_logger
from vlrscraper.resource import Resource
from vlrscraper import constants as const
from vlrscraper.utils import get_url_segment
from vlrscraper.scraping import XpathParser, join


if TYPE_CHECKING:
    from vlrscraper.player import Player

_logger = get_logger()


class Team:
    resource = Resource("https://vlr.gg/team/<res_id>")

    def __init__(
        self,
        _id: int,
        name: Optional[str],
        tag: Optional[str],
        logo: Optional[str],
        roster: Optional[List[Player]],
    ) -> None:
        if not isinstance(_id, int) or _id <= 0:
            raise ValueError("Player ID must be an integer {0 < ID}")

        self.__id = _id
        self.__name = name
        self.__tag = tag
        self.__logo = logo
        self.__roster = roster

    def __eq__(self, other: object) -> bool:
        _logger.warning(
            "Avoid using inbuilt equality for Team. See Team.is_same_team() and Team.is_same_roster()"
        )
        return object.__eq__(self, other)

    def is_same_team(self, other: object) -> bool:
        """Check if this team's org is the same organization as the other team.

        Purely checks attributes related to the actual organization itself (ID, name, tag, logo) rather than
        attributes that change over time such as roster

        Parameters
        ----------
        other : object
            The other team to check

        Returns
        -------
        bool
            `True` if all attributes (ID, name, tag, logo) match, else `False`
        """
        return (
            isinstance(other, Team)
            and self.__id == other.__id
            and self.__name == other.__name
            and self.__tag == other.__tag
        )

    def has_same_roster(self, other: object) -> bool:
        """Check if all of the players / staff on this team are the same as the other team

        Does not include the player's current team in the equality check, only whether
        the roster contains the same actual players

        Parameters
        ----------
        other : object
            The other team to check

        Returns
        -------
        bool
            _description_
        """

        if not isinstance(other, Team):
            return False

        mR, oR = self.get_roster(), other.get_roster()

        return (
            isinstance(other, Team)
            and mR is None is oR
            or (
                not (mR is None or oR is None)
                and len(mR) == len(oR)
                and all([p.is_same_player(oR[i])] for i, p in enumerate(mR))
            )
        )

    def __repr__(self) -> str:
        return (
            f"Team({self.get_id()}"
            + f", {self.get_name()}" * bool(self.get_name())
            + f", {self.get_tag()}" * bool(self.get_tag())
            + f", {self.get_logo()}" * bool(self.get_logo())
            + f", {0 if (r := self.get_roster()) is None else [p.get_display_name() for p in r]}"
            * bool(r)
            + ")"
        )

    def get_id(self) -> int:
        """Get the vlr ID of this team

        Returns
        -------
        int
            vlr ID
        """
        return self.__id

    def get_name(self) -> Optional[str]:
        """Get the name of this team

        Returns
        -------
        str
            The name of the team
        """
        return self.__name

    def get_tag(self) -> Optional[str]:
        """Get the 1-3 letter team tag of this team

        Returns
        -------
        str
            The team tag
        """
        return self.__tag

    def get_logo(self) -> Optional[str]:
        """Get the URL of this team's logo

        Returns
        -------
        str
            The team logo
        """
        return self.__logo

    def get_roster(self) -> Optional[List[Player]]:
        """Get the list of players / staff for this team

        Returns
        -------
        list[Player]
            The team roster
        """
        return self.__roster

    def set_roster(self, roster: List[Player]) -> None:
        self.__roster = roster

    def add_to_roster(self, player: Player) -> None:
        if self.__roster is None:
            self.__roster = []

        self.__roster.append(player)

    @staticmethod
    def from_team_page(
        _id: int, name: str, tag: str, logo: str, roster: List[Player]
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
        return Team(_id, name, tag, logo, roster)

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
        return Team(_id, name=name, tag=None, logo=logo, roster=None)

    @staticmethod
    def from_match_page(
        _id: int, name: str, tag: str, logo: str, roster: List[Player]
    ) -> Team:
        return Team(_id, name, tag, logo, roster)

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

        from vlrscraper.player import Player

        team = Team.from_team_page(
            _id,
            parser.get_text(const.TEAM_DISPLAY_NAME),
            parser.get_text(const.TEAM_TAG),
            f"https:{parser.get_img(const.TEAM_IMG)}",
            [],
        )
        team.set_roster(Player.get_players_from_team_page(parser, team))

        return team

    @staticmethod
    def get_team_from_player_page(parser: XpathParser) -> Team:
        imgpath = join(const.PLAYER_CURRENT_TEAM, "img")[2:]
        namepath = join(const.PLAYER_CURRENT_TEAM, "div[2]", "div[1]")[2:]

        team_name = parser.get_text(namepath)
        team_image = f"https:{parser.get_img(imgpath)}"
        team_id = get_url_segment(
            parser.get_href(const.PLAYER_CURRENT_TEAM), 2, rtype=int
        )

        return Team.from_player_page(team_id, team_name, team_image)
