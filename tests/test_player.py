# type: ignore
import pytest

from vlrscraper.player import Player, PlayerStatus
from vlrscraper.team import Team


def test_player_init():
    # Correct exceptions
    with pytest.raises(ValueError):
        Player(0, None, None, None, None, None, None)

    with pytest.raises(ValueError):
        Player(-100, None, None, None, None, None, None)

    with pytest.raises(ValueError):
        Player("4004", None, None, None, None, None, None)

    with pytest.raises(ValueError):
        Player(None, None, None, None, None, None, None)

    benjy = Player(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team().is_same_team(
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        )
    )
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"
    assert benjy.get_status() == PlayerStatus.ACTIVE

    # No forename OR surname
    crappy = Player(31207, None, None, None, None, None, None)
    assert crappy.get_name() is None

    # Forename but no surname
    crappy = Player(31207, None, None, "Lee", None, None, None)
    assert crappy.get_name() == "Lee"


def test_player_equals():
    benjy = Player(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert benjy.is_same_player(benjy)
    assert not benjy.is_same_player(1)

    benjy2 = Player(
        298731,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )

    # Different ID, different object
    assert not benjy.is_same_player(benjy2)

    # Different object, same ID
    benjy3 = Player(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert benjy.is_same_player(benjy3)

    assert benjy == benjy
    assert benjy != benjy2


def test_string():
    benjy = Player(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert (
        str(benjy)
        == "Player(29873, benjyfishy, Benjamin Fish, https://owcdn.net/img/665b77ca4bc4d.png, Team Heretics, ACTIVE)"
    )


def test_player_from():
    benjy = Player.from_player_page(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    benjy = Player.from_team_page(
        29873,
        "benjyfishy",
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        ),
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    benjy = Player.from_match_page(29873, "Benjyfishy")

    assert benjy.get_name() is benjy.get_current_team() is benjy.get_status() is None


def test_player_get(requests_regression):
    # Average player
    benjy = Player.get_player(29873)
    assert benjy is not None
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team().is_same_team(
        Team.from_player_page(
            1001, "Team Heretics", "https://owcdn.net/img/637b755224c12.png"
        )
    )
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"
    assert benjy.get_status() == PlayerStatus.ACTIVE

    # Player with non-latin characters in name
    crappy = Player.get_player(31207)
    assert crappy is not None
    assert crappy.get_id() == 31207
    assert crappy.get_display_name() == "Carpe"
    assert crappy.get_current_team().is_same_team(
        Team.from_player_page(14, "T1", "https://owcdn.net/img/62fe0b8f6b084.png")
    )
    assert crappy.get_name() == "Lee Jae-hyeok"
    assert crappy.get_image() == "https://owcdn.net/img/65cc6f0f4da99.png"
    assert crappy.get_status() == PlayerStatus.ACTIVE

    # Bad player very bad
    assert Player.get_player(None) is None
    assert Player.get_player(31207.0) is None
    assert Player.get_player("1000") is None

    # Inactive player
    assert Player.get_player(45).get_status() == PlayerStatus.INACTIVE
