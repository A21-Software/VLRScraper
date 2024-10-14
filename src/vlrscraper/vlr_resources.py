from vlrscraper.resource import Resource


def vlr_url(subdomain: str) -> str:
    return f"https://vlr.gg/{subdomain}"


player_resource = Resource(vlr_url("player/<res_id>"))
player_teams_resource = Resource(vlr_url("player/matches/<res_id>"))
team_resource = Resource(vlr_url("team/<res_id>"))
match_resource = Resource(vlr_url("<res_id>"))


def player_match_resource(page: int) -> Resource:
    return Resource(vlr_url(f"player/matches/<res_id>?page={page}"))
