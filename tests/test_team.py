from vlrscraper.team import Team
from vlrscraper.player import Player, PlayerStatus

from .helpers import assert_players


def test_team_init():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen.get_id() == 2
    assert sen.get_name() == "Sentinels"
    assert sen.get_tag() == "SEN"
    assert sen.get_logo() == "https://owcdn.net/img/62875027c8e06.png"
    assert sen.get_roster() == []


def test_teamEq():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen == sen

    sen2 = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen == sen2

    sen3 = Team(2, "Heretics", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])

    assert sen != sen3


def test_teamRepr():
    sen = Team(2, "Sentinels", "SEN", "https://owcdn.net/img/62875027c8e06.png", [])
    assert str(sen) == "Sentinels / SEN, [https://owcdn.net/img/62875027c8e06.png]"


def test_getTeam():
    # Valid team
    sen = Team.get_team(2)
    assert sen.get_id() == 2
    assert sen.get_name() == "Sentinels"
    assert sen.get_logo() == "https://owcdn.net/img/62875027c8e06.png"
    assert len(sen.get_roster()) == 8
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
        sen.get_roster()[4],
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
