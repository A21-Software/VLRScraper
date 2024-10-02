from vlrscraper.player import Player
from vlrscraper.team import Team


def assert_players(player: Player, player2: Player) -> None:
    assert player.get_name() == player2.get_name()
    assert player.get_id() == player2.get_id()
    assert player.get_current_team() == player2.get_current_team()
    assert player.get_display_name() == player2.get_display_name()
    assert player.get_image() == player2.get_image()
    assert player.get_status() == player2.get_status()


def assert_teams(team: Team, team2: Team) -> None:
    assert team.get_name() == team2.get_name()
    assert team.get_id() == team2.get_id()
    assert team.get_logo() == team2.get_id()
