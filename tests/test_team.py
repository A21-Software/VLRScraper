# type: ignore
import pytest

from vlrscraper.team import Team
from vlrscraper.player import Player, PlayerStatus

from .helpers import assert_players


def test_team_init():
    with pytest.raises(ValueError):
        Team(0, None, None, None, None)
    with pytest.raises(ValueError):
        Team(-100, None, None, None, None)
    with pytest.raises(ValueError):
        Team("4004", None, None, None, None)
    with pytest.raises(ValueError):
        Team(4004.0, None, None, None, None)

    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen.get_id() == 2
    assert sen.get_name() == "Sentinels"
    assert sen.get_tag() == "SEN"
    assert sen.get_logo() == "https://owcdn.net/img/62875027c8e06.png"
    assert sen.get_roster() == []

    sen = Team(2, "Sentinels", "SEN", "", None)
    assert sen.get_roster() is None


def test_teamEq():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen.is_same_team(sen) is True
    assert sen.has_same_roster(sen) is True
    assert sen == sen

    sen2 = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen.is_same_team(sen) is True
    assert sen.has_same_roster(sen) is True
    assert sen != sen2

    sen2.set_roster([Player.from_match_page(4004, "Zekken")])
    assert sen.is_same_team(sen2) is True
    assert sen.has_same_roster(sen2) is False

    sen3 = Team(2, "Heretics", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen.is_same_team(sen3) is False
    assert sen.has_same_roster(sen3) is True

    assert not sen.is_same_team("sen")
    assert not sen.has_same_roster("sen")


def test_teamRoster():
    sen = Team.from_player_page(2, "Sentinels", "")
    sen.add_to_roster(Player.from_match_page(2, "Zekken"))

    assert sen.get_roster()[0].is_same_player(Player.from_match_page(2, "Zekken"))


def test_teamRepr():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])
    assert (
        str(sen) == "Team(2, Sentinels, SEN, https://owcdn.net/img/62875027c8e06.png)"
    )

    sen.add_to_roster(Player.from_match_page(4004, "Zekken"))
    assert (
        str(sen)
        == "Team(2, Sentinels, SEN, https://owcdn.net/img/62875027c8e06.png, ['Zekken'])"
    )


""" def test_teamRoster():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])
    sen.set_roster([Player.from_match_page(4004, "Zekken"), Player.from_match_page(2, "TenZ")])

    assert sen.get_roster() == [Player.from_match_page(4004, "Zekken"), Player.from_match_page(2, "TenZ")]

    sen.add_to_roster(Player.from_match_page(3, "johnqt"))
    assert sen.get_roster() == [Player.from_match_page(4004, "Zekken"), Player.from_match_page(2, "TenZ"), Player.from_match_page(3, "johnqt")] """


def test_getTeam(requests_regression):
    # Valid team
    sen = Team.get_team(2)
    assert sen is not None
    assert sen.get_id() == 2
    assert sen.get_name() == "Sentinels"
    assert sen.get_logo() == "https://owcdn.net/img/62875027c8e06.png"
    assert len(sen.get_roster()) == 10
    assert_players(
        sen.get_roster()[0],
        Player.from_team_page(
            1265,
            "johnqt",
            "Mohamed",
            "Ouarid",
            sen,
            "https://owcdn.net/img/65622aa13dc03.png",
            PlayerStatus.ACTIVE,
        ),
    )

    assert_players(
        sen.get_roster()[6],
        Player.from_team_page(
            45,
            "SicK",
            "Hunter",
            "Mims",
            sen,
            "https://owcdn.net/img/6399a54fc4472.png",
            PlayerStatus.INACTIVE,
        ),
    )

    # Invalid team
    assert Team.get_team(-100) is None
    assert Team.get_team("2") is None
