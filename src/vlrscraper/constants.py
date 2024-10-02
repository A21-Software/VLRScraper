from .scraping import xpath, join


PLAYER_DISPLAYNAME = xpath("h1", class_="wf-title")
PLAYER_FULLNAME = xpath("h2", class_="player-real-name")
PLAYER_IMAGE_SRC = join(xpath("div", class_="wf-avatar"), "img")
PLAYER_CURRENT_TEAM = f"({xpath('a', class_='wf-module-item mod-first')})[1]"
