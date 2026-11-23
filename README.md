# SportStatsAPI examples – sports data API code for Python, JavaScript and curl

Copy-paste code for the [SportStatsAPI](https://sportstatsapi.com/) sports data API: fixtures, results, live scores and standings for popular leagues in curl, Python and JavaScript, plus one small runnable script per league. All examples work with a free key.

## Leagues

- [Premier League API examples](premier-league/README.md): football (soccer), England, league code `l30`, script: Premier League table to CSV
- [NBA API examples](nba/README.md): basketball, USA, league code `l1jy`, script: NBA results into SQLite
- [NFL API examples](nfl/README.md): American football, USA, league code `l53v`, script: One NFL week of scores to JSON
- [NHL API examples](nhl/README.md): ice hockey, USA, league code `l49f`, script: NHL results with OT and shootouts to CSV
- [KHL API examples](khl/README.md): ice hockey, Russia, league code `l49c`, script: KHL results with OT and shootouts to CSV

## Quick start

- [Create a free account](https://account.sportstatsapi.com/signup) and confirm the e-mail link. Your key starts with `sk_live_` and is shown once.
- Put it in an environment variable: `export SSA_API_KEY=sk_live_...`
- Send it as a bearer token. Every call is a GET under `https://api.sportstatsapi.com/api/v1`.

curl: today's live hockey scores:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches/live" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Find any league's code without a key: `/coverage/{sport}/{league}` takes our code or the competition key.

curl (no key):

```bash
curl -s https://api.sportstatsapi.com/api/v1/coverage/soccer/england--premier-league
```

Then run a script, for example the Premier League table to CSV:

Run:

```bash
git clone https://github.com/ownthegame/sportstatsapi-examples
cd sportstatsapi-examples/examples/premier-league
python3 table_to_csv.py > table.csv
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Add a league

Every page is generated from one entry in `leagues.json` (league code, sport, dates for the examples, a trimmed real response). Add an entry, run `python3 build.py`, and the page, its README and the sitemap are written.

## Links

- [API reference](https://sportstatsapi.com/docs/api/) and [quickstart](https://sportstatsapi.com/docs/quickstart/)
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

Code in this repository is MIT licensed. The API data is not: it is used under the SportStatsAPI [terms](https://sportstatsapi.com/legal/terms/).

[Data: SportStatsAPI](https://sportstatsapi.com/)
