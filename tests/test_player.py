from vlrscraper.player import Player


def test_player_init():
    benjy = Player(
        29873,
        "benjyfishy",
        1001,
        "Benjamin",
        "Fish",
        "https://owcdn.net/img/665b77ca4bc4d.png",
    )
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team() == 1001
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"


def test_player_get():
    # Average player
    benjy = Player.get_player(29873)
    assert benjy.get_id() == 29873
    assert benjy.get_display_name() == "benjyfishy"
    assert benjy.get_current_team() == 1001
    assert benjy.get_name() == "Benjamin Fish"
    assert benjy.get_image() == "https://owcdn.net/img/665b77ca4bc4d.png"

    # Player with non-latin characters in name
    crappy = Player.get_player(31207)
    assert crappy.get_id() == 31207
    assert crappy.get_display_name() == "Carpe"
    assert crappy.get_current_team() == 14
    assert crappy.get_name() == "Lee Jae-hyeok"
    assert crappy.get_image() == "https://owcdn.net/img/65cc6f0f4da99.png"
