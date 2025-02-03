![tests](https://github.com/A21-Software/VLRScraper/actions/workflows/test.yml/badge.svg)
![quality](https://github.com/A21-Software/VLRScraper/actions/workflows/quality.yml/badge.svg)
![pypi](https://img.shields.io/pypi/v/vlrscraper)

### General Usage

If you don't care about the inner workings of the module and just want to use it to get JSON data from vlr.gg, all you
need to look at are `vlrscraper.match`, `vlrscraper.team` and `vlrscraper.player`.

###### Getting Matches

Getting a matches data from a match ID is as simple as
```
vlrscraper.match.get_match(vlr_id)
```

Getting a number of matches from their match IDs can be done by using
```
vlrscraper.match.get_matches(vlr_ids)
```

this uses a threaded match scraper to scrape in parallel. I'll add options to configure this soon
