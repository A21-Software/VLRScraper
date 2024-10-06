# type: ignore
from vlrscraper.match import Match, PlayerStats
from vlrscraper.team import Team

from .helpers import assert_teams


def test_match_init():
    m = Match(
        408415,
        "NA Play-ins: Grand Final",
        "Red Bull Home Ground #5",
        100,
        (
            Team.from_match_page(2, "Sentinels", "", "", []),
            Team.from_match_page(188, "Cloud9", "", "", []),
        ),
    )
    assert m.get_id() == 408415
    assert m.get_name() == "NA Play-ins: Grand Final"
    assert m.get_event_name() == "Red Bull Home Ground #5"
    assert m.get_full_name() == "Red Bull Home Ground #5 - NA Play-ins: Grand Final"
    assert m.get_date() == 100
    assert m.get_teams()[0].is_same_team(
        Team.from_match_page(2, "Sentinels", "", "", [])
    )


def test_match_eq():
    m = Match(
        408415,
        "NA Play-ins: Grand Final",
        "Red Bull Home Ground #5",
        100,
        (
            Team.from_match_page(2, "Sentinels", "", "", []),
            Team.from_match_page(188, "Cloud9", "", "", []),
        ),
    )
    assert m.is_same_match(m)

    assert not m.is_same_match("NA Play-ins")
    assert not m.is_same_match(10)

    assert m == m
    assert m != 10


def test_match_get():
    # Current match
    m = Match.get_match(408415)
    assert m is not None
    assert m.get_id() == 408415
    assert m.get_name() == "NA Play-ins: Grand Final"
    assert m.get_event_name() == "Red Bull Home Ground #5"
    assert m.get_full_name() == "Red Bull Home Ground #5 - NA Play-ins: Grand Final"
    assert m.get_date() == 1727660400.0

    assert (
        m.get_player_stats(4004)
        == m.get_stats()[4004]
        == PlayerStats(1.19, 271, 45, 36, 8, 9, 71, 164, 21, 7, 5, 2)
    )

    assert_teams(
        m.get_teams()[0],
        Team.from_match_page(
            2, "Sentinels", "", "https://owcdn.net/img/62875027c8e06.png", []
        ),
    )

    # China match (no stats)
    m = Match.get_match(370727)
    assert m is not None
    assert m.get_player_stats(3520) == PlayerStats(
        None, 204, 77, 82, 20, -5, None, 131, 24, 18, 25, -7
    )

    # Old match (no stats)
    m = Match.get_match(3490)
    assert m is not None
    assert m.get_player_stats(4004) == PlayerStats(
        None, 176, 13, 17, 8, -4, None, 112, 28, 2, 1, 1
    )

    assert Match.get_match(0) is None
    assert Match.get_match("3490") is None
