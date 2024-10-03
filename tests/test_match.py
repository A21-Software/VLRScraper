from vlrscraper.match import Match, MatchStats
from vlrscraper.team import Team


def test_match_init():
    m = Match(
        408415,
        "NA Play-ins: Grand Final",
        "Red Bull Home Ground #5",
        100,
        (Team(2, "Sentinels", "", ""), Team(188, "Cloud9", "", "")),
    )
    assert m.get_id() == 408415
    assert m.get_name() == "NA Play-ins: Grand Final"
    assert m.get_event_name() == "Red Bull Home Ground #5"
    assert m.get_full_name() == "Red Bull Home Ground #5 - NA Play-ins: Grand Final"
    assert m.get_date() == 100
    assert m.get_teams() == (Team(2, "Sentinels", "", ""), Team(188, "Cloud9", "", ""))

def test_match_eq():
    m = Match(
        408415,
        "NA Play-ins: Grand Final",
        "Red Bull Home Ground #5",
        100,
        (Team(2, "Sentinels", "", ""), Team(188, "Cloud9", "", "")),
    )
    assert m == m

def test_match_get():
    # Current match
    m = Match.get_match(408415)
    assert m.get_id() == 408415
    assert m.get_name() == "NA Play-ins: Grand Final"
    assert m.get_event_name() == "Red Bull Home Ground #5"
    assert m.get_full_name() == "Red Bull Home Ground #5 - NA Play-ins: Grand Final"
    assert m.get_date() == 1727660400.0

    assert m.get_player_stats(4004) == MatchStats(
        1.19, 271, 45, 36, 8, 9, 71, 164, 21, 7, 5, 2
    )

    """ assert m.get_teams() == (
        Team(2, "Sentinels", "", "https://owcdn.net/img/62875027c8e06.png"),
        Team(188, "Cloud9", "", "https://owcdn.net/img/628addcbd509e.png"),
    ) """

    # China match (no stats)
    m = Match.get_match(370727)
    assert m.get_player_stats(3520) == MatchStats(
        None, 204, 77, 82, 20, -5, None, 131, 24, 18, 25, -7
    )

    # Old match (no stats)
    m = Match.get_match(3490)
    assert m.get_player_stats(4004) == MatchStats(
        None, 176, 13, 17, 8, -4, None, 112, 28, 2, 1, 1
    )
