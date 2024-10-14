"""Contains XPATH constants for scraping"""

from .scraping import xpath, join


PLAYER_DISPLAYNAME = xpath("h1", class_="wf-title")
PLAYER_FULLNAME = xpath("h2", class_="player-real-name")
PLAYER_IMAGE_SRC = join(xpath("div", class_="wf-avatar"), "img")
PLAYER_CURRENT_TEAM = f"({xpath('a', class_='wf-module-item mod-first')})[1]"
PLAYER_INACTIVE_CHECK = "(//a[contains(@class, 'wf-module-item mod-first')])[1]//div[contains(@class, 'ge-text-light')]"

PLAYER_MATCHES = xpath("a", class_="wf-card")
PLAYER_MATCH_DATES = join(PLAYER_MATCHES, xpath("div", class_="m-item-date"))

TEAM_DISPLAY_NAME = xpath("h1", class_="wf-title")
TEAM_TAG = xpath("h2", class_="team-header-tag")
TEAM_IMG = join(xpath("div", class_="wf-avatar"), "img")
TEAM_ROSTER_ITEMS = join(xpath("div", class_="team-roster-item"), "a")
TEAM_ROSTER_ITEM_ALIAS = xpath("div", class_="team-roster-item-name-alias")
TEAM_ROSTER_ITEM_FULLNAME = xpath("div", class_="team-roster-item-name-real")
TEAM_ROSTER_ITEM_IMAGE = join(xpath("div", class_="team-roster-item-img"), "img")

TEAM_MATCHES = (
    "//a[contains(@class, 'wf-card') and not(contains(@class, 'm-item-games-item'))]"
)
TEAM_MATCH_DATES = join(TEAM_MATCHES, xpath("div", class_="m-item-date"))

MATCH_EVENT_NAME = "(//a[contains(@class, 'match-header-event')]//div//div)[1]"
MATCH_NAME = "(//a[contains(@class, 'match-header-event')]//div//div)[2]"

MATCH_TEAMS = xpath("a", class_="match-header-link")

MATCH_TEAM_NAMES = join(MATCH_TEAMS, xpath("div", class_="wf-title-med"))
MATCH_TEAM_LOGOS = join(MATCH_TEAMS, "img")

MATCH_DATE = "//div[@class='moment-tz-convert'][1]"

MATCH_PLAYER_TABLE = "//div[@class='vm-stats-game mod-active']//tbody//tr//td//a"
MATCH_PLAYER_NAMES = join(MATCH_PLAYER_TABLE, "div[1]")
MATCH_PLAYER_STATS = "//div[@class='vm-stats-game mod-active']//tbody//tr//td//span[contains(@class, 'mod-both')]"
