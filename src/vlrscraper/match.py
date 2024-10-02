from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

from lxml import html

from vlrscraper.resource import Resource
from vlrscraper import constants as const
from vlrscraper.scraping import XpathParser

if TYPE_CHECKING:
    from vlrscraper.team import Team


@dataclass
class MatchStats:
    rating: float
    ACS: int
    kills: int
    deaths: int
    assists: int
    KD: int
    KAST: int
    ADR: int
    HS: int
    FK: int
    FD: int
    plants: int
    defuses: int


class Match:
    resource = Resource("https://vlr.gg/<res_id>")

    def __init__(
        self,
        _id: int,
        match_name: str,
        event_name: str,
        epoch: float,
        teams: tuple[Team, Team] = [],
    ) -> None:
        self.__id = _id
        self.__name = match_name
        self.__event = event_name
        self.__epoch = epoch
        self.__teams = teams
        self.__stats: dict[int, MatchStats] = {}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Match)
            and self.get_id() == other.get_id()
            and self.get_full_name() == other.get_full_name()
            and self.get_date() == other.get_date()
            and self.get_teams() == other.get_teams()
        )

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_event_name(self) -> str:
        return self.__event

    def get_full_name(self) -> str:
        return f"{self.__event} - {self.__name}"

    def get_teams(self) -> list[Team]:
        return self.__teams

    def get_stats(self) -> list[MatchStats]:
        return self.__stats

    def get_player_stats(self, player: int) -> Optional[MatchStats]:
        return self.__stats.get(player, None)

    def get_date(self) -> float:
        return self.__epoch

    def __parse_match_stats(
        players: list[int], stats: list[html.HtmlElement]
    ) -> dict[int, MatchStats]:
        if len(stats) // 14 != 0:
            return []
        stats = {}
        TO_LOAD = [float, int, int, int, int, int, int, int, int, int, int, int]
        for i, player in enumerate(players):
            indexes = range(i * 14, (i + 1) * 14)

            stats.update(
                {player: MatchStats(*[TO_LOAD(stats[stat].text) for stat in indexes])}
            )
        return stats

    @staticmethod
    def get_match(_id: int) -> Optional[Match]:
        data = Match.resource.get_data(_id)

        if data["success"] is False:
            return None

        parser = XpathParser(data["data"])

        match_players = parser.get_text_many(const.MATCH_PLAYER_TABLE)
        match_stats = parser.get_elements(const.MATCH_PLAYER_STATS)
        match_stats_parsed = Match.__parse_match_stats(match_players, match_stats)
        print(match_stats_parsed)

        match = Match(
            _id,
            parser.get_text(const.MATCH_NAME),
            parser.get_text(const.MATCH_EVENT_NAME),
        )

        return match
