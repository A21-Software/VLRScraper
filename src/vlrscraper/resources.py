from __future__ import annotations

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, List, Tuple

from vlrscraper.logger import get_logger

_logger = get_logger()


class PlayerStatus(IntEnum):
    """Contains data relating to the player's current status.
    Can be either INACTIVE or ACTIVE
    """

    INACTIVE = 1
    ACTIVE = 2


class Player:
    """Encapsulates all data relating to individual valorant players

    :param _id: The vlr.gg ID of the player
    :type _id: int

    :param name: The display name of the player
    :type name: str, optional

    :param current_team: The current team the player is on
    :type current_team: Team, optional

    :param forename: The forename of the player
    :type forename: str, optional

    :param surname: The surname of the player
    :type surname: str, optional

    :param image: The url of an image of the player
    :type image: str, optional

    :param status: The status of the player, either ACTIVE or INACTIVE
    :type status: PlayerStatus, optional
    """

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
        """Player constructor"""

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
        """Get the vlr.gg ID of this player

        :return: The vlr.gg ID
        :rtype: int
        """
        return self.__id

    def get_display_name(self) -> Optional[str]:
        """Get the display name of the player

        :return: The display name of the player
        :rtype: Optional[str]
        """
        return self.__displayname

    def get_current_team(self) -> Optional[Team]:
        """Get the current team of the player

        :return: The current team
        :rtype: Team
        """
        return self.__current_team

    def get_name(self) -> Optional[str]:
        """Get the real name of the player

        :return: The forename and surname
        :rtype: str, optional
        """
        return " ".join(self.__name) if self.__name is not None else None

    def get_image(self) -> Optional[str]:
        """Get the absolute url of the player's image

        :return: The player's image url
        :rtype: str, optional
        """
        return self.__image_src

    def get_status(self) -> Optional[PlayerStatus]:
        """Get the status of the player

        :return: The status, either ACTIVE or INACTIVE
        :rtype: :class:`vlrscraper.resources.PlayerStatus`
        """
        return self.__status

    def is_same_player(self, other: object) -> bool:
        """Check if this player is the same person as another player

        This involves checking the id, name, display tag and image, but `not` the current team or current status

        :param other: The other player to check
        :type other: object

        :return: Whether both players represent the same `physical` player
        :rtype: bool
        """
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
        """Construct a Player object from the data available on a vlr.gg player page

        :param _id: The vlr.gg ID of the player
        :type _id: int

        :param display_name: The display name of the player
        :type display_name: str

        :param forename: The forename of the player
        :type forename: str

        :param surname: The surname of the player
        :type surname: str, optional

        :param current_team: The current team the player is on
        :type current_team: Team


        :param image: The url of an image of the player
        :type image: str

        :param status: The status of the player, either ACTIVE or INACTIVE
        :type status: PlayerStatus

        :return: The player object constructed
        :rtype: Player
        """
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
        """Construct a Player object from the data available on a vlr.gg team page

        :param _id: The vlr.gg ID of the player
        :type _id: int

        :param display_name: The display name of the player
        :type display_name: str

        :param forename: The forename of the player
        :type forename: str

        :param surname: The surname of the player
        :type surname: str, optional

        :param current_team: The current team the player is on
        :type current_team: Team


        :param image: The url of an image of the player
        :type image: str

        :param status: The status of the player, either ACTIVE or INACTIVE
        :type status: PlayerStatus

        :return: The player object constructed
        :rtype: Player
        """
        return Player(_id, display_name, current_team, forename, surname, image, status)

    @staticmethod
    def from_match_page(_id: int, display_name: str) -> Player:
        """Construct a Player object from the data available on a vlr.gg match page

        :param _id: The vlr.gg ID of the player
        :type _id: int

        :param display_name: The display name of the player
        :type display_name: str

        :return: The Player object constructed
        :rtype: Player
        """
        return Player(_id, display_name, None, None, None, None, None)


class Team:
    """Encapsulates all data relating to valorant teams

    :param _id: The vlr.gg ID of the team
    :type _id: int

    :param name: The name of the team
    :type name: Optional[str]

    :param tag: The display tag of the team
    :type tag: Optional[str]

    :param logo: The URL of the team's logo
    :type logo: Optional[str]

    :param roster: The current roster of the team
    :type roster: Optional[List[Player]]
    """

    # TODO implement Roster object
    def __init__(
        self,
        _id: int,
        name: Optional[str],
        tag: Optional[str],
        logo: Optional[str],
        roster: Optional[List[Player]],
    ) -> None:
        """Team constructor"""
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

    def is_same_team(self, other: object) -> bool:
        """Check if this team's org is the same organization as the other team.

        Purely checks attributes related to the actual organization itself (ID, name, tag, logo) rather than
        attributes that change over time such as roster

        :param other: The other team to check
        :type other: object

        :return: True if the teams match otherwise False
        :rtype: bool
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

        :param other: The other team to check
        :type other: object

        :return: True if the teams have the same roster, otherwise False
        :rtype: bool
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

    def get_id(self) -> int:
        """Get the vlr.gg ID of this team

        :return: The vlr ID
        :rtype: int
        """
        return self.__id

    def get_name(self) -> Optional[str]:
        """Get the name of this team

        :return: The display name of the team
        :rtype: str, optional
        """
        return self.__name

    def get_tag(self) -> Optional[str]:
        """Get the 1-3 letter team tag of this team

        :return: The team display tag
        :rtype: str, optional
        """
        return self.__tag

    def get_logo(self) -> Optional[str]:
        """Get the absolute url of this team's logo

        :return: The team's logo
        :rtype: str, optional
        """
        return self.__logo

    def get_roster(self) -> Optional[List[Player]]:
        """Get the list of players / staff for this team

        :return: The players / staff on the current roster
        :rtype: List[Player], optional
        """
        return self.__roster

    def set_roster(self, roster: List[Player]) -> None:
        """Set the current roster of this team

        :param roster: The players / staff to add
        :type roster: List[Player], optional
        """
        self.__roster = roster

    def add_to_roster(self, player: Player) -> None:
        if self.__roster is None:
            self.__roster = []
        self.__roster.append(player)

    @staticmethod
    def from_team_page(
        _id: int, name: str, tag: str, logo: str, roster: List[Player]
    ) -> Team:
        """Construct a Team object from the data available on the team's vlr.gg page

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :param name: The full name of the team
        :type name: str

        :param tag: The 1-3 character team tag
        :type tag: str

        :param logo: The absolute url of the team's logo
        :type logo: str

        :param roster: The list of players / staff currently on the team
        :type roster: List[Player]

        :return: The team constructed
        :rtype: Team
        """
        return Team(_id, name, tag, logo, roster)

    @staticmethod
    def from_player_page(_id: int, name: str, logo: str) -> Team:
        """Construct a Team object from the data available on the team's vlr.gg page

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :param name: The full name of the team
        :type name: str

        :param logo: The absolute url of the team's logo
        :type logo: str

        :return: The team constructed
        :rtype: Team
        """
        return Team(_id, name=name, tag=None, logo=logo, roster=None)

    @staticmethod
    def from_match_page(
        _id: int, name: str, tag: str, logo: str, roster: List[Player]
    ) -> Team:
        """Construct a Team object from the data available on the team's vlr.gg page

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :param name: The full name of the team
        :type name: str

        :param tag: The 1-3 character team tag
        :type tag: str

        :param logo: The absolute url of the team's logo
        :type logo: str

        :param roster: The list of players / staff currently on the team
        :type roster: List[Player]

        :return: The team constructed
        :rtype: Team
        """
        return Team(_id, name, tag, logo, roster)


@dataclass
class PlayerStats:
    """Encapsulates the stats of a single player over a map / match

    :param rating: Vlr.gg rating
    :type rating: float
    :param ACS: Average combat store
    :type ACS: int
    :param kills: Kills
    :type kills: int
    :param deaths: Deaths
    :type deaths: int
    :param assists: Assists
    :type assists: int
    :param KD: Kill / Death ratio expressed as k - d
    :type KD: int
    :param KAST: Kill-Assist-Survive-Trade percentage
    :type KAST: int
    :param ADR: Average damage per round
    :type ADR: int
    :param HS: Headshot percentage (0-100)
    :type HS: int
    :param FK: First kills
    :type FK: int
    :param FD: First deaths
    :type FD: int
    :param FKFD: First kills / First death expressed as fk - fd
    :type FKFD: int
    """

    rating: Optional[float]
    ACS: Optional[int]
    kills: Optional[int]
    deaths: Optional[int]
    assists: Optional[int]
    KD: Optional[int]
    KAST: Optional[int]
    ADR: Optional[int]
    HS: Optional[int]
    FK: Optional[int]
    FD: Optional[int]
    FKFD: Optional[int]


class Match:
    """Encapsulates all data related to valorant matches

    :param _id: The vlr.gg ID of the match
    :type _id: int

    :param match_name: The name of the match
    :type match_name: str

    :param event_name: The name of the event the match was a part of
    :type event_name: str

    :param epoch: The epoch at which the match took place
    :type epoch: float

    :param teams: The two teams involved in the match
    :type teams: Tuple[Team, Team] | Tuple[()], by default ()
    """

    def __init__(
        self,
        _id: int,
        match_name: str,
        event_name: str,
        epoch: float,
        teams: Tuple[Team, Team] | Tuple[()] = (),
    ) -> None:
        self.__id = _id
        self.__name = match_name
        self.__event = event_name
        self.__epoch = epoch
        self.__teams = teams
        self.__stats: dict[int, PlayerStats] = {}

    def __eq__(self, other: object) -> bool:
        _logger.warning(
            "Avoid using inbuilt equality for Matches. See Match.is_same_match()"
        )
        return object.__eq__(self, other)

    def is_same_match(self, other: object) -> bool:
        """Check if this match is the same match as another.
        This includes the ID, name, date, teams and rosters

        :param other: The other match to compare to
        :type other: object

        :return: True if the matches are the same else False
        """
        return (
            isinstance(other, Match)
            and self.get_id() == other.get_id()
            and self.get_full_name() == other.get_full_name()
            and self.get_date() == other.get_date()
            and all(
                team.is_same_team(other.get_teams()[i])
                and team.has_same_roster(other.get_teams()[i])
                for i, team in enumerate(self.get_teams())
            )
        )

    def get_id(self) -> int:
        """Get the vlr.gg ID of this match

        :return: The ID of the match
        :rtype: int
        """
        return self.__id

    def get_name(self) -> str:
        """Get the name of this match

        :return: The match name
        :rtype: str
        """
        return self.__name

    def get_event_name(self) -> str:
        """Get the name of the event this match was a part of

        :return: The event name
        :rtype: str
        """
        return self.__event

    def get_full_name(self) -> str:
        """Gets the full name (event name `and` match name) of the match

        :return: The full name
        :rtype: str
        """
        return f"{self.__event} - {self.__name}"

    def get_teams(self) -> Tuple[Team, Team] | Tuple[()]:
        """Gets the two teams involved in the match

        :return: The teams
        :rtype: Union[Tuple[Team, Team] | Tuple[()]]
        """
        return self.__teams

    def get_stats(self) -> dict[int, PlayerStats]:
        """Get the stats for the match

        :return: A mapping of player IDs to stats
        :rtype: dict[int, PlayerStats]
        """
        return self.__stats

    def get_player_stats(self, player: int) -> Optional[PlayerStats]:
        """Gets the match stats for a specific player

        :param player: The vlr.gg ID of the player to get the stats for
        :type player: int

        :return: The player's stats, or None if the player was not part of the match
        :rtype: Optional[PlayerStats]
        """
        return self.__stats.get(player, None)

    def get_date(self) -> float:
        """Get the match epoch

        :return: The match epoch
        :rtype: float
        """
        return self.__epoch

    def set_stats(self, stats: dict[int, PlayerStats]):
        """Set the player stats dictionary

        :param stats: The stat data
        :type stats: dict[int, PlayerStats]
        """
        self.__stats = stats

    def add_match_stat(self, player: int, stats: PlayerStats) -> None:
        """Add a player's stats to the match

        :param player: The vlr.gg ID of the player
        :type player: int

        :param stats: The stats of the player
        :type stats: PlayerStats
        """
        self.__stats.update({player: stats})
