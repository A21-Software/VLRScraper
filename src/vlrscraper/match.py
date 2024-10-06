from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, List, Tuple

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
class PlayerStats:
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
    resource = Resource("https://vlr.gg/<res_id>")

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
            "Avoid using inbuilt equality for Players. See Match.is_same_match()"
        )
        return object.__eq__(self, other)

    def is_same_match(self, other: object) -> bool:
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
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_event_name(self) -> str:
        return self.__event

    def get_full_name(self) -> str:
        return f"{self.__event} - {self.__name}"

    def get_teams(self) -> Tuple[Team, Team] | Tuple[()]:
        return self.__teams

    def get_stats(self) -> dict[int, PlayerStats]:
        return self.__stats

    def get_player_stats(self, player: int) -> Optional[PlayerStats]:
        return self.__stats.get(player, None)

    def get_date(self) -> float:
        return self.__epoch

    def set_stats(self, stats: dict[int, PlayerStats]):
        self.__stats = stats

    def add_match_stat(self, player: int, stats: PlayerStats) -> None:
        self.__stats.update({player: stats})

    @staticmethod
    def __parse_match_stats(
        players: List[int], stats: List[html.HtmlElement]
    ) -> dict[int, PlayerStats]:
        if len(stats) % 12 != 0:
            _logger.warning(f"Wrong amount of stats passed ({len(stats)})")
            return {}
        player_stats = {}
        for i, player in enumerate(players):
            player_stats.update(
                {
                    player: PlayerStats(
                        parse_stat(stats[i * 12 + 0].text, rtype=float),
                        parse_stat(stats[i * 12 + 1].text, rtype=int),
                        parse_stat(stats[i * 12 + 2].text, rtype=int),
                        parse_stat(stats[i * 12 + 3].text, rtype=int),
                        parse_stat(stats[i * 12 + 4].text, rtype=int),
                        parse_stat(stats[i * 12 + 5].text, rtype=int),
                        parse_stat(stats[i * 12 + 6].text, rtype=int),
                        parse_stat(stats[i * 12 + 7].text, rtype=int),
                        parse_stat(stats[i * 12 + 8].text, rtype=int),
                        parse_stat(stats[i * 12 + 9].text, rtype=int),
                        parse_stat(stats[i * 12 + 10].text, rtype=int),
                        parse_stat(stats[i * 12 + 11].text, rtype=int),
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

        teams = (
            Team.from_match_page(
                get_url_segment(team_links[0], 2, int),
                team_names[0],
                "",
                f"https:{team_logos[0]}",
                [
                    Player.from_match_page(match_player_ids[pl], match_player_names[pl])
                    for pl in range(0, 5)
                ],
            ),
            Team.from_match_page(
                get_url_segment(team_links[1], 2, int),
                team_names[1],
                "",
                f"https:{team_logos[1]}",
                [
                    Player.from_match_page(match_player_ids[pl], match_player_names[pl])
                    for pl in range(1, 5)
                ],
            ),
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
