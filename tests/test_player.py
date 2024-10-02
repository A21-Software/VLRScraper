from vlrscraper.player import Player, PlayerStatus
from vlrscraper.team import Team


def test_player_init():
    benjy = Player(
        29873,
        "benjyfishy",
        1001,
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team() == 1001
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"
    assert benjy.get_status() == PlayerStatus.ACTIVE


def test_player_equals():
    benjy = Player(
        29873,
        "benjyfishy",
        1001,
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert benjy == benjy
    assert benjy != 1

    benjy2 = Player(
        298731,
        "benjyfishy",
        1001,
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )

    assert benjy != benjy2


def test_string():
    benjy = Player(
        29873,
        "benjyfishy",
        1001,
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
        PlayerStatus.ACTIVE,
    )
    assert (
        str(benjy)
        == "benjyfishy (Benjamin Fish) [https://owcdn.net/img/665b77ca4bc4d.png]"
    )


def test_player_get():
    # Average player
    benjy = Player.get_player(29873)
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team() == Team(
        1001, "Team Heretics", "", "https://owcdn.net/img/637b755224c12.png"
    )
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"
    assert benjy.get_status() == PlayerStatus.ACTIVE

    # Player with non-latin characters in name
    crappy = Player.get_player(31207)
    assert crappy.get_id() == 31207
    assert crappy.get_display_name() == "Carpe"
    assert crappy.get_current_team() == Team(
        14, "T1", "", "https://owcdn.net/img/62fe0b8f6b084.png"
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
