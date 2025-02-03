![tests](https://github.com/A21-Software/VLRScraper/actions/workflows/test.yml/badge.svg)
![quality](https://github.com/A21-Software/VLRScraper/actions/workflows/quality.yml/badge.svg)
![pypi](https://img.shields.io/pypi/v/vlrscraper)

# General Usage

If you don't care about the inner workings of the module and just want to use it to get JSON data from vlr.gg, all you
need to look at are `vlrscraper.match`, `vlrscraper.team` and `vlrscraper.player`.

### Getting Match Data

To get a matches data by its vlr match ID, use
```
vlrscraper.match.get_match(vlr_id)
```

<details>
<summary>Match Format</summary>
  ```
{vlr_id: {
  "teams": {team_id: team_data, ...},
  "players": {player_id: player_data, ...},
  "match": {
    "name": match_name,
    "event": match_event,
    "timestamp": match_epoch,
    "stats: match_stats
  }
  }
}
  ```
</details>

Getting a number of matches from their match IDs can be done by using
```
vlrscraper.match.get_matches(vlr_ids)
```

this uses a threaded match scraper to scrape in parallel. I'll add options to configure this soon

### Getting Player Data

Getting a player's data from an ID can be done using
```
vlrscraper.player.get_player(vlr_id)
```
this gets a player's current team, name, IGN, photo. To get team data relating to players, see [Getting Team Data](#getting-team-data).
For getting match data relating to a specific player, see [Getting Match Data](#getting-match-data)

### Getting Team Data
