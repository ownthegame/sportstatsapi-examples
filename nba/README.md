# NBA API – free JSON examples (Python, JavaScript, curl)

NBA games, final scores with quarter-by-quarter points, live scores and the standings by conference and division as JSON. Tip-off times are in UTC, so an evening game in New York shows up on the next UTC date: ask for a date range, not a single day, when you want one US night of games.

- League code: `l1jy` (sport path `/basketball`)
- Free plan: the current season. Paid plans: every season we store (results from 2010-10-03, box scores from 2017-10-01, play-by-play from 2025-01-01, as reported by the public coverage endpoint on 2026-11-23).
- League page: [NBA data API on SportStatsAPI](https://sportstatsapi.com/coverage/basketball/usa/nba/)

## Setup

[Sign up free](https://account.sportstatsapi.com/signup) (confirm the e-mail link), copy your key once, and keep it out of your code: put it in an environment variable. Call the API from a server or script, never from browser code, where anyone can read the key.

Shell:

```bash
export SSA_API_KEY=sk_live_your_key_here
```

Python setup used below (pip install requests):

```python
import os
import requests

BASE = "https://api.sportstatsapi.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SSA_API_KEY']}"}
```

The JavaScript snippets use the built-in `fetch` of Node 18+; save them as `.mjs` files so top-level `await` works.

## Fixtures for a date range

Upcoming NBA matches between two dates (inclusive, UTC). Without dates the list covers today only.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/basketball/matches?league_id=l1jy&date_from=2026-11-25&date_to=2026-11-27" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/basketball/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l1jy", "date_from": "2026-11-25", "date_to": "2026-11-27"})
r.raise_for_status()
for m in r.json()["data"]:
    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l1jy", date_from: "2026-11-25", date_to: "2026-11-27" });
const res = await fetch(`${BASE}/basketball/matches?${q}`, { headers });
const { data } = await res.json();
for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);
```

## Results

Finished matches, newest first. Keep the rows whose `status_code` starts with "final". A finished game has `status` "Finished" and `status_code` "final". `periods` lists Q1 to Q4; after overtime one OT entry holds every overtime together, so the periods always add up to the final score.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/basketball/matches?league_id=l1jy&date_from=2026-11-21&date_to=2026-11-23&order=desc" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/basketball/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l1jy", "date_from": "2026-11-21", "date_to": "2026-11-23", "order": "desc"})
for m in r.json()["data"]:
    if m["status_code"].startswith("final"):
        h, a = m["home_team"], m["away_team"]
        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l1jy", date_from: "2026-11-21", date_to: "2026-11-23", order: "desc" });
const { data } = await (await fetch(`${BASE}/basketball/matches?${q}`, { headers })).json();
for (const m of data.filter((m) => m.status_code.startsWith("final"))) {
  console.log(m.start_date, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
}
```

## Live scores

`/basketball/matches/live` returns every live basketball match of all leagues in one list, so filter on `league_code`. On the Free plan live scores are up to 15 minutes behind; poll once a minute at most (5 requests a minute is the Free cap).

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/basketball/matches/live" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/basketball/matches/live", headers=HEADERS, timeout=30)
live = [m for m in r.json()["data"] if m["league_code"] == "l1jy"]
for m in live:
    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",
          m["away_team"]["score"], m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/basketball/matches/live`, { headers })).json();
const live = data.filter((m) => m.league_code === "l1jy");
for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
```

## Standings

The current table in one request. Standings come as conferences, each with its divisions and their teams. A row has won, lost, games behind (`gb`), win percentage, home and road records, streak and the last 10 games.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/basketball/leagues/l1jy/standings" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/basketball/leagues/l1jy/standings", headers=HEADERS, timeout=30)
table = r.json()["data"]
for conf in table["standings"]["category"]["league"]:
    for div in conf["division"]:
        for row in div["team"]:
            print(conf["name"], div["name"], row["name"], row["won"], "-", row["lost"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/basketball/leagues/l1jy/standings`, { headers })).json();
for (const conf of data.standings.category.league) {
  for (const div of conf.division) {
    for (const row of div.team) console.log(div.name, row.name, `${row.won}-${row.lost}`);
  }
}
```

## Real response, trimmed

One finished NBA match from `/basketball/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`.

JSON:

```json
{
  "code": "moak0",
  "league_code": "l1jy",
  "status": "Finished",
  "status_code": "final",
  "start_at": "2026-11-22T00:30:00Z",
  "home_team": {
    "code": "tm5t",
    "name": "New York Knicks",
    "score": 97
  },
  "away_team": {
    "code": "tmpi",
    "name": "Portland Trail Blazers",
    "score": 96
  },
  "periods": [
    {
      "period": "1",
      "label": "Q1",
      "home": 40,
      "away": 23
    },
    {
      "period": "2",
      "label": "Q2",
      "home": 26,
      "away": 20
    },
    {
      "period": "3",
      "label": "Q3",
      "home": 15,
      "away": 29
    },
    {
      "period": "4",
      "label": "Q4",
      "home": 16,
      "away": 24
    }
  ]
}
```

And the first row of the standings (structure kept, other rows cut):

JSON:

```json
{
  "league": [
    {
      "name": "Eastern Conference",
      "division": [
        {
          "name": "Atlantic",
          "team": [
            {
              "position": "1",
              "name": "Philadelphia 76ers",
              "display_name": "Philadelphia 76ers",
              "won": "12",
              "lost": "3",
              "gb": "-",
              "percentage": ".800",
              "home_record": "6-2",
              "road_record": "6-1",
              "average_points_for": "114.1",
              "average_points_agains": "111.3",
              "difference": "+2.8",
              "streak": "W3",
              "last_10": "8-2",
              "code": "tm5p"
            }
          ]
        }
      ]
    }
  ]
}
```

## Paging and coverage

`limit` goes up to 100 (default 50); use `offset` and `meta.total` to page through longer lists. What a league has (live scores, box scores, play-by-play, history) is public, no key needed:

curl (no key):

```bash
curl -s https://api.sportstatsapi.com/api/v1/coverage/basketball/l1jy
```

## Runnable example: NBA results into SQLite

[examples/nba/results_to_sqlite.py](../examples/nba/results_to_sqlite.py): Pulls the finished games of a date range (default: the last 3 days, UTC) and upserts them into a local SQLite file keyed by the match `code`, with the quarter scores as JSON. Run it every morning and the table grows into your own season log; running it twice never creates duplicates. Python 3.8+, standard library only.

Run:

```bash
cd examples/nba
export SSA_API_KEY=sk_live_your_key_here
python3 results_to_sqlite.py --from 2026-11-20 --to 2026-11-23 --db nba.sqlite
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Links

- [NBA on SportStatsAPI](https://sportstatsapi.com/coverage/basketball/usa/nba/): coverage, data and plans for this league
- [Free basketball API](https://sportstatsapi.com/developers/free-basketball-api/)
- [API reference](https://sportstatsapi.com/docs/api/) and [quickstart](https://sportstatsapi.com/docs/quickstart/)
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

[Data: SportStatsAPI](https://sportstatsapi.com/)
