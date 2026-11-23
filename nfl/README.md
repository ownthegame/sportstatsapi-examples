# NFL API – free JSON examples (Python, JavaScript, curl)

NFL schedule, final scores by quarter, live scores and the standings by conference and division as JSON. Match answers carry no week number, so a week of games is simply a date range: Thursday to the following Tuesday in UTC catches the Thursday, Sunday and Monday night games.

- League code: `l53v` (sport path `/american-football`)
- Free plan: the current season. Paid plans: every season we store (results from 2016-09-09, box scores from 2016-09-11, play-by-play from 2016-09-09, as reported by the public coverage endpoint on 2026-11-23).
- League page: [NFL data API on SportStatsAPI](https://sportstatsapi.com/coverage/american-football/usa/nfl/)

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

Upcoming NFL matches between two dates (inclusive, UTC). Without dates the list covers today only.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/american-football/matches?league_id=l53v&date_from=2026-11-26&date_to=2026-12-01" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/american-football/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l53v", "date_from": "2026-11-26", "date_to": "2026-12-01"})
r.raise_for_status()
for m in r.json()["data"]:
    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l53v", date_from: "2026-11-26", date_to: "2026-12-01" });
const res = await fetch(`${BASE}/american-football/matches?${q}`, { headers });
const { data } = await res.json();
for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);
```

## Results

Finished matches, newest first. Keep the rows whose `status_code` starts with "final". A finished game has `status` "Finished" and `status_code` "final"; a game that went to overtime gets an OT entry in `periods`.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/american-football/matches?league_id=l53v&date_from=2026-11-19&date_to=2026-11-24&order=desc" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/american-football/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l53v", "date_from": "2026-11-19", "date_to": "2026-11-24", "order": "desc"})
for m in r.json()["data"]:
    if m["status_code"].startswith("final"):
        h, a = m["home_team"], m["away_team"]
        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l53v", date_from: "2026-11-19", date_to: "2026-11-24", order: "desc" });
const { data } = await (await fetch(`${BASE}/american-football/matches?${q}`, { headers })).json();
for (const m of data.filter((m) => m.status_code.startsWith("final"))) {
  console.log(m.start_date, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
}
```

## Live scores

`/american-football/matches/live` returns every live American football match of all leagues in one list, so filter on `league_code`. On the Free plan live scores are up to 15 minutes behind; poll once a minute at most (5 requests a minute is the Free cap).

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/american-football/matches/live" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/american-football/matches/live", headers=HEADERS, timeout=30)
live = [m for m in r.json()["data"] if m["league_code"] == "l53v"]
for m in live:
    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",
          m["away_team"]["score"], m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/american-football/matches/live`, { headers })).json();
const live = data.filter((m) => m.league_code === "l53v");
for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
```

## Standings

The current table in one request. Standings come as the two conferences, each with four divisions. A row has won, lost, ties, win percentage, home, road, division and conference records, points for and against and the streak.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/american-football/leagues/l53v/standings" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/american-football/leagues/l53v/standings", headers=HEADERS, timeout=30)
table = r.json()["data"]
for conf in table["standings"]["category"]["league"]:
    for div in conf["division"]:
        for row in div["team"]:
            print(div["name"], row["name"], row["won"], row["lost"], row["ties"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/american-football/leagues/l53v/standings`, { headers })).json();
for (const conf of data.standings.category.league) {
  for (const div of conf.division) {
    for (const row of div.team) console.log(div.name, row.name, `${row.won}-${row.lost}-${row.ties}`);
  }
}
```

## Real response, trimmed

One finished NFL match from `/american-football/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`.

JSON:

```json
{
  "code": "mn17c",
  "league_code": "l53v",
  "status": "Finished",
  "status_code": "final",
  "start_at": "2026-11-20T01:15:00Z",
  "home_team": {
    "code": "t1025",
    "name": "Houston Texans",
    "score": 26
  },
  "away_team": {
    "code": "t102d",
    "name": "Indianapolis Colts",
    "score": 3
  },
  "periods": [
    {
      "period": "1",
      "label": "Q1",
      "home": 7,
      "away": 3
    },
    {
      "period": "2",
      "label": "Q2",
      "home": 10,
      "away": 0
    },
    {
      "period": "3",
      "label": "Q3",
      "home": 9,
      "away": 0
    },
    {
      "period": "4",
      "label": "Q4",
      "home": 0,
      "away": 0
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
      "name": "American Football Conference",
      "division": [
        {
          "name": "AFC East",
          "team": [
            {
              "position": "1",
              "name": "Buffalo Bills",
              "display_name": "Buffalo Bills",
              "won": "8",
              "lost": "1",
              "ties": "0",
              "win_percentage": ".889",
              "home_record": "3-1",
              "road_record": "5-0",
              "division_record": "1-1",
              "conference_record": "5-1",
              "points_for": "287",
              "points_against": "199",
              "difference": "+88",
              "streak": "W5",
              "code": "t101x"
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
curl -s https://api.sportstatsapi.com/api/v1/coverage/american-football/l53v
```

## Runnable example: One NFL week of scores to JSON

[examples/nfl/week_scores_json.py](../examples/nfl/week_scores_json.py): Fetches every finished game between two dates (default: the last 7 days, UTC) and writes a compact JSON file: teams, final score, quarter scores and kickoff time. Small enough to ship with a static site or a bot. Python 3.8+, standard library only.

Run:

```bash
cd examples/nfl
export SSA_API_KEY=sk_live_your_key_here
python3 week_scores_json.py --from 2026-11-19 --to 2026-11-24 --out week.json
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Links

- [NFL on SportStatsAPI](https://sportstatsapi.com/coverage/american-football/usa/nfl/): coverage, data and plans for this league
- [Free American football API](https://sportstatsapi.com/developers/free-american-football-api/)
- [API reference](https://sportstatsapi.com/docs/api/) and [quickstart](https://sportstatsapi.com/docs/quickstart/)
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

[Data: SportStatsAPI](https://sportstatsapi.com/)
