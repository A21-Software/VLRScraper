from typing import Optional, List, Tuple, Dict

import time
from lxml import html

import vlrscraper.constants as const
from vlrscraper.logger import get_logger
from vlrscraper.scraping import XpathParser, join, ThreadedMatchScraper
from vlrscraper.resources import Player, PlayerStatus, Team, PlayerStats, Match
from vlrscraper.vlr_resources import (
    team_resource,
    match_resource,
    player_resource,
    player_match_resource,
)
from vlrscraper.utils import (
    parse_stat,
    get_url_segment,
    resolve_vlr_image,
    epoch_from_timestamp,
    parse_first_last_name,
)

_logger = get_logger()


class PlayerController:
    """Contains all methods for scraping player data"""

    @staticmethod
    def get_player(_id: int) -> Optional[Player]:
        """Scrape a player's data given a valid vlr.gg player ID

        .. code-block:: python

            benjyfishy_data = get_player(29873)

            get_player(-1) == None # True

        :param _id: The ID of the player
        :type _id: int

        :return: The player data
        :rtype: Optional[Player]
        """
        if (parser := player_resource.get_parser(_id)) is None:
            return None

        player_alias = parser.get_text(const.PLAYER_DISPLAYNAME)
        player_image = f"https:{parser.get_img(const.PLAYER_IMAGE_SRC)}"
        player_name = parse_first_last_name(parser.get_text(const.PLAYER_FULLNAME))
        player_status = (
            PlayerStatus.ACTIVE
            if len(parser.get_elements(const.PLAYER_INACTIVE_CHECK)) <= 2
            else PlayerStatus.INACTIVE
        )

        from vlrscraper.controllers import TeamController

        return Player.from_player_page(
            _id,
            player_alias,
            player_name[0],
            player_name[-1],
            TeamController.get_team_from_player_page(parser=parser),
            player_image,
            player_status,
        )

    @staticmethod
    def get_players_from_team_page(parser: XpathParser, team: Team) -> List[Player]:
        """Scrape the player data from a team's vlr.gg page

        .. code-block:: python

            # Get all the EDG players from the champs 2024 grand final
            edg_parser = team_resource.get_parser(378829)
            edg_players = PlayerController.get_players_from_team_page(edg_parser, TeamController.from_parser(edg_parser))

        :param parser: The page's XPathParser
        :type parser: XpathParser

        :param team: The team that the players are a part of
        :type team: Team

        :return: A list of players that are present on the team vlr.gg page
        :rtype: List[Player]
        """
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


class TeamController:
    """Contains all methods relating to scraping Team data"""

    @staticmethod
    def get_team(_id: int) -> Optional[Team]:
        """Scrape the team data from vlr.gg given a valid team ID

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :return: The team data, or None if the ID is invalid
        :rtype: Optional[Team]
        """

        if (parser := team_resource.get_parser(_id)) is None:
            return None

        from vlrscraper.controllers import PlayerController

        team = Team.from_team_page(
            _id,
            parser.get_text(const.TEAM_DISPLAY_NAME),
            parser.get_text(const.TEAM_TAG),
            f"https:{parser.get_img(const.TEAM_IMG)}",
            [],
        )
        team.set_roster(PlayerController.get_players_from_team_page(parser, team))

        return team

    @staticmethod
    def get_team_from_player_page(parser: XpathParser, index: int = 1) -> Team:
        """_summary_

        :param parser: _description_
        :type parser: XpathParser
        :param index: _description_, defaults to 1
        :type index: int, optional
        :return: _description_
        :rtype: Team
        """
        imgpath = join(const.PLAYER_CURRENT_TEAM, "img")[2:]
        namepath = join(const.PLAYER_CURRENT_TEAM, "div[2]", "div[1]")[2:]

        team_name = parser.get_text(namepath)
        team_image = f"https:{parser.get_img(imgpath)}"
        team_id = get_url_segment(
            parser.get_href(const.PLAYER_CURRENT_TEAM), 2, rtype=int
        )

        return Team.from_player_page(team_id, team_name, team_image)

    @staticmethod
    def get_player_team_history(_id: int) -> List[Team]:
        if (parser := player_resource.get_parser(_id)) is None:
            return []

        parsed_teams: List[Team] = []

        team = 1
        while team_link := parser.get_href(f"{const.PLAYER_TEAMS}[{team}]"):
            team_id = get_url_segment(team_link, 2, int)
            team_name = parser.get_text(f"{const.PLAYER_TEAMS}[{team}]//div[2]//div[1]")
            team_image = parser.get_img(f"{const.PLAYER_TEAMS}[{team}]//img")
            parsed_teams.append(
                Team.from_player_page(team_id, team_name, resolve_vlr_image(team_image))
            )
            team += 1

        return parsed_teams


class MatchController:
    @staticmethod
    def __parse_match_stats(
        players: List[int], stats: List[html.HtmlElement]
    ) -> Dict[int, PlayerStats]:
        """Parse the match stats on the given match page

        :param players: The players to parse the stats for
        :type players: List[int]

        :param stats: A list of html.HtmlElement each representing a table row from the stat page
        :type stats: List[html.HtmlElement]

        :return: A dictionary mapping player IDs to PlayerStats objects
        :rtype: dict[int, PlayerStats]
        """
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
    def parse_match(_id: int, data: bytes) -> Match:
        """Parse a vlr.gg match page from the bytes returned by :func:`requests.get`

        :param _id: The match ID
        :type _id: int

        :param data: The byte data of the match page
        :type data: bytes

        :return: The match data
        :rtype: Match
        """
        parser = XpathParser(data)

        match_player_ids = [
            get_url_segment(str(x), 2, rtype=int)
            for x in parser.get_elements(const.MATCH_PLAYER_TABLE, "href")
        ]
        match_player_names = parser.get_text_many(const.MATCH_PLAYER_NAMES)
        match_stats = parser.get_elements(const.MATCH_PLAYER_STATS)

        match_stats_parsed = MatchController.__parse_match_stats(
            match_player_ids, match_stats
        )  # type: ignore

        team_links = parser.get_elements(const.MATCH_TEAMS, "href")
        team_names = parser.get_text_many(const.MATCH_TEAM_NAMES)
        team_logos = parser.get_elements(const.MATCH_TEAM_LOGOS, "src")
        _logger.debug(team_logos)

        teams = (
            Team.from_match_page(
                get_url_segment(str(team_links[0]), 2, int),
                team_names[0],
                "",
                f"https:{team_logos[0]}",
                [
                    Player.from_match_page(match_player_ids[pl], match_player_names[pl])
                    for pl in range(0, 5)
                ],
            ),
            Team.from_match_page(
                get_url_segment(str(team_links[1]), 2, int),
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

    @staticmethod
    def get_match(_id: int) -> Optional[Match]:
        """Scrape the data of a match given a valid vlr.gg match ID

        :param _id: The ID of the match
        :type _id: int

        :return: The match data
        :rtype: Optional[Match]
        """
        if (data := match_resource.get_data(_id))["success"] is False:
            return None
        return MatchController.parse_match(_id, data["data"])

    @staticmethod
    def __get_player_match_ids_page(
        _id: int, page: int = 1
    ) -> Tuple[List[int], List[float]]:
        if (parser := player_match_resource(page).get_parser(_id)) is None:
            get_logger().warning(f"Could not get player match page for player {_id}")
            return ([], [])
        match_epochs = [
            epoch_from_timestamp(f"{elem} -0400", "%Y/%m/%d%I:%M %p %z")
            for elem in parser.get_text_many(const.PLAYER_MATCH_DATES)
        ]
        match_ids = [
            get_url_segment(str(elem), 1, rtype=int)
            for elem in parser.get_elements(const.PLAYER_MATCHES, "href")
        ]
        return match_ids, match_epochs

    @staticmethod
    def __get_team_match_ids_page(
        _id: int, page: int = 1
    ) -> Tuple[List[int], List[float]]:
        if (parser := team_resource.get_parser(_id)) is None:
            return ([], [])

        match_epochs = [
            epoch_from_timestamp(f"{elem} -0400", "%Y/%m/%d%I:%M %p %z")
            for elem in parser.get_text_many(const.TEAM_MATCH_DATES)
        ]
        match_ids = [
            get_url_segment(str(elem), 1, rtype=int)
            for elem in parser.get_elements(const.TEAM_MATCHES, "href")
        ]
        return match_ids, match_epochs

    @staticmethod
    def get_player_match_ids(
        _id: int, _from: float, to: float = time.time()
    ) -> List[int]:
        """Get a list of vlr.gg match IDs that a player has been a part of, within the given timeframe

        :param _id: The vlr.gg ID of the player
        :type _id: int

        :param _from: The epoch to get the matches from
        :type _from: float

        :param to: The epoch to get matches to, defaults to time.time()
        :type to: float, optional

        :return: A list of match IDs of the matches that occurred between the two given timestamps
        :rtype: List[Match]
        """
        page = 1
        ids, epochs = MatchController.__get_player_match_ids_page(_id, page)
        _logger.warning(ids)

        parsed_ids: List[int] = []

        while (
            len(
                parsed_ids := parsed_ids
                + [id for i, id in enumerate(ids) if _from <= epochs[i] <= to]
            )
            % 50
            == 0
            and parsed_ids != []
        ):
            _logger.warning(len(parsed_ids))
            page += 1
            ids, epochs = MatchController.__get_player_match_ids_page(_id, page)
        return parsed_ids

    @staticmethod
    def get_team_match_ids(
        _id: int, _from: float, to: float = time.time()
    ) -> List[int]:
        """Get a list of vlr.gg match IDs that a team has been a part of, within the given timeframe

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :param _from: The epoch to get the matches from
        :type _from: float

        :param to: The epoch to get matches to, defaults to time.time()
        :type to: float, optional

        :return: A list of match IDs of the matches that occurred between the two given timestamps
        :rtype: List[Match]
        """
        page = 1
        ids, epochs = MatchController.__get_team_match_ids_page(_id, page)

        parsed_ids: List[int] = []

        while (
            len(
                parsed_ids := parsed_ids
                + [id for i, id in enumerate(ids) if _from <= epochs[i] <= to]
            )
            % 50
            == 0
            and parsed_ids != []
        ):
            _logger.warning(len(parsed_ids))
            page += 1
            ids, epochs = MatchController.__get_player_match_ids_page(_id, page)

        return parsed_ids

    @staticmethod
    def get_player_matches(
        _id: int, _from: float, to: float = time.time()
    ) -> List[Match]:
        """Get a player's valorant matches within the given timeframe

        :param _id: The vlr.gg ID of the player
        :type _id: int

        :param _from: The epoch to get the matches from
        :type _from: float

        :param to: The epoch to get matches to, defaults to time.time()
        :type to: float, optional

        :return: A list of matches that occurred between the two given timestamps
        :rtype: List[Match]
        """
        match_ids = MatchController.get_player_match_ids(_id, _from, to)
        # Thread get each one
        scraper = ThreadedMatchScraper(match_ids)
        matches = scraper.run()
        return matches

    @staticmethod
    def get_team_matches(
        _id: int, _from: float, to: float = time.time()
    ) -> List[Match]:
        """Get a teams valorant matches within the given timeframe

        :param _id: The vlr.gg ID of the team
        :type _id: int

        :param _from: The epoch to get the matches from
        :type _from: float

        :param to: The epoch to get matches to, defaults to time.time()
        :type to: float, optional

        :return: A list of matches that occurred between the two given timestamps
        :rtype: List[Match]
        """
        match_ids = MatchController.get_team_match_ids(_id, _from, to)
        scraper = ThreadedMatchScraper(match_ids)
        matches = scraper.run()
        return matches
