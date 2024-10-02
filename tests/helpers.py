from vlrscraper.player import Player


def assert_players(player: Player, player2: Player) -> None:
    assert player.get_name() == player2.get_name()
    assert player.get_id() == player2.get_id()
    assert player.get_current_team() == player2.get_current_team()
    assert player.get_display_name() == player2.get_display_name()
    assert player.get_image() == player2.get_image()
    assert player.get_status() == player2.get_status()
