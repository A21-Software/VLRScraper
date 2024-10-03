from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from lxml import html

from vlrscraper.resource import Resource
from vlrscraper.logger import get_logger
from vlrscraper import constants as const
from vlrscraper.scraping import XpathParser
from vlrscraper.utils import get_url_segment, epoch_from_timestamp, parse_stat

if TYPE_CHECKING:
    from vlrscraper.team import Team

_logger = get_logger()


@dataclass
class MatchStats:
    rating: float | None
    ACS: int
    kills: int
    deaths: int
    assists: int
    KD: int
    KAST: int | None
    ADR: int
    HS: int
    FK: int
    FD: int
    FKFD: int


class Match:
    resource = Resource("https://vlr.gg/<res_id>")

    def __init__(
        self,
        _id: int,
        match_name: str,
        event_name: str,
        epoch: float,
        teams: tuple[Team, Team] | tuple[()] = (),
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

    def get_teams(self) -> tuple[Team, Team] | tuple[()]:
        return self.__teams

    def get_stats(self) -> dict[int, MatchStats]:
        return self.__stats

    def get_player_stats(self, player: int) -> Optional[MatchStats]:
        return self.__stats.get(player, None)

    def get_date(self) -> float:
        return self.__epoch

    def set_stats(self, stats: dict[int, MatchStats]):
        self.__stats = stats

    def add_match_stat(self, player: int, stats: MatchStats) -> None:
        self.__stats.update({player: stats})

    @staticmethod
    def __parse_match_stats(
        players: list[int], stats: list[html.HtmlElement]
    ) -> dict[int, MatchStats]:
        if len(stats) % 12 != 0:
            _logger.warning(f"Wrong amount of stats passed ({len(stats)})")
            return {}
        player_stats = {}
        TO_LOAD = [
            float,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
        ]
        for i, player in enumerate(players):
            indexes = range(i * 12, (i + 1) * 12)

            player_stats.update(
                {
                    player: MatchStats(
                        *[
                            parse_stat(stats[stat].text, rtype=TO_LOAD[stat % 12])
                            for stat in indexes
                        ]
                    )
                }
            )
        return player_stats

    @staticmethod
    def get_match(_id: int) -> Optional[Match]:
        data = Match.resource.get_data(_id)

        if data["success"] is False:
            return None

        parser = XpathParser(data["data"])

        match_player_ids = [
            get_url_segment(x, 2, rtype=int)
            for x in parser.get_elements(const.MATCH_PLAYER_TABLE, "href")
        ]
        match_player_names = parser.get_text_many(const.MATCH_PLAYER_NAMES)
        match_stats = parser.get_elements(const.MATCH_PLAYER_STATS)
        match_stats_parsed = Match.__parse_match_stats(match_player_ids, match_stats)

        team_links = parser.get_elements(const.MATCH_TEAMS, "href")
        team_names = parser.get_text_many(const.MATCH_TEAM_NAMES)
        team_logos = parser.get_elements(const.MATCH_TEAM_LOGOS, "src")
        _logger.debug(team_logos)

        from vlrscraper.team import Team
        from vlrscraper.player import Player

        teams = tuple(
            Team.from_match_page(
                get_url_segment(team, 2, int),
                team_names[i],
                "",
                f"https:{team_logos[i]}",
                [
                    Player.from_match_page(match_player_ids[pl], match_player_names[pl])
                    for pl in range(i * 5, (i + 1) * 5)
                ],
            )
            for i, team in enumerate(team_links)
        )

        match = Match(
            _id,
            parser.get_text(const.MATCH_NAME),
            parser.get_text(const.MATCH_EVENT_NAME),
            epoch_from_timestamp(
                f'{parser.get_elements(const.MATCH_DATE, "data-utc-ts")[0]} -0400',
                "%Y-%m-%d %H:%M:%S %z",
            ),
            teams,
        )
        match.set_stats(match_stats_parsed)

        return match
