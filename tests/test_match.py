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


def test_match_get():
    m = Match.get_match(408415)
    assert m.get_id() == 408415
    assert m.get_name() == "NA Play-ins: Grand Final"
    assert m.get_event_name() == "Red Bull Home Ground #5"
    assert m.get_full_name() == "Red Bull Home Ground #5 - NA Play-ins: Grand Final"
    assert m.get_date() == 100
    assert m.get_teams() == (
        Team(2, "Sentinels", "", "https://owcdn.net/img/62875027c8e06.png"),
        Team(188, "Cloud9", "", "https://owcdn.net/img/628addcbd509e.png"),
    )
