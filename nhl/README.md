# NHL API – free JSON examples (Python, JavaScript, curl)

NHL games, final scores by period, overtime and shootout results, live scores and the standings by conference and division as JSON. Shootout games are easy to spot: they have their own `status_code`, so you can count regulation, overtime and shootout wins without parsing text.

- League code: `l49f` (sport path `/hockey`)
- Free plan: the current season. Paid plans: every season we store (results from 2016-10-12, box scores from 2016-10-15, play-by-play from 2016-10-12, as reported by the public coverage endpoint on 2026-11-23).
- League page: [NHL data API on SportStatsAPI](https://sportstatsapi.com/coverage/hockey/usa/nhl/)

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

Upcoming NHL matches between two dates (inclusive, UTC). Without dates the list covers today only.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches?league_id=l49f&date_from=2026-11-24&date_to=2026-11-26" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l49f", "date_from": "2026-11-24", "date_to": "2026-11-26"})
r.raise_for_status()
for m in r.json()["data"]:
    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l49f", date_from: "2026-11-24", date_to: "2026-11-26" });
const res = await fetch(`${BASE}/hockey/matches?${q}`, { headers });
const { data } = await res.json();
for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);
```

## Results

Finished matches, newest first. Keep the rows whose `status_code` starts with "final". `status_code` tells how a game ended: "final" (regulation), "final_overtime" or "final_penalties" (shootout). `periods` lists P1 to P3, then OT and SO when they were played. Take the final score from `home_team.score` and `away_team.score`: in a shootout game the SO entry may be the shootout tally, so the periods do not always add up to the final.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches?league_id=l49f&date_from=2026-11-20&date_to=2026-11-22&order=desc" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l49f", "date_from": "2026-11-20", "date_to": "2026-11-22", "order": "desc"})
for m in r.json()["data"]:
    if m["status_code"].startswith("final"):
        h, a = m["home_team"], m["away_team"]
        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l49f", date_from: "2026-11-20", date_to: "2026-11-22", order: "desc" });
const { data } = await (await fetch(`${BASE}/hockey/matches?${q}`, { headers })).json();
for (const m of data.filter((m) => m.status_code.startsWith("final"))) {
  console.log(m.start_date, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
}
```

## Live scores

`/hockey/matches/live` returns every live ice hockey match of all leagues in one list, so filter on `league_code`. On the Free plan live scores are up to 15 minutes behind; poll once a minute at most (5 requests a minute is the Free cap).

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches/live" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/matches/live", headers=HEADERS, timeout=30)
live = [m for m in r.json()["data"] if m["league_code"] == "l49f"]
for m in live:
    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",
          m["away_team"]["score"], m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/hockey/matches/live`, { headers })).json();
const live = data.filter((m) => m.league_code === "l49f");
for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
```

## Standings

The current table in one request. Standings come as conferences, each with its divisions. A row has games played, won, lost, overtime losses, points, regulation-plus-overtime wins, shootout wins and losses, home and road records, goals for and against, last ten and streak.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/leagues/l49f/standings" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/leagues/l49f/standings", headers=HEADERS, timeout=30)
table = r.json()["data"]
for conf in table["standings"]["category"]["league"]:
    for div in conf["division"]:
        for row in div["team"]:
            print(div["name"], row["name"], row["points"], "pts")
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/hockey/leagues/l49f/standings`, { headers })).json();
for (const conf of data.standings.category.league) {
  for (const div of conf.division) {
    for (const row of div.team) console.log(div.name, row.name, row.points, "pts");
  }
}
```

## Real response, trimmed

One finished NHL match from `/hockey/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`.

JSON:

```json
{
  "code": "mo2l1",
  "league_code": "l49f",
  "status": "After Penalties",
  "status_code": "final_penalties",
  "start_at": "2026-11-20T00:00:00Z",
  "home_team": {
    "code": "tt3y",
    "name": "Toronto Maple Leafs",
    "score": 3
  },
  "away_team": {
    "code": "tt4m",
    "name": "Los Angeles Kings",
    "score": 4
  },
  "periods": [
    {
      "period": "1",
      "label": "P1",
      "home": 2,
      "away": 0
    },
    {
      "period": "2",
      "label": "P2",
      "home": 1,
      "away": 3
    },
    {
      "period": "3",
      "label": "P3",
      "home": 0,
      "away": 0
    },
    {
      "period": "OT",
      "label": "OT",
      "home": 0,
      "away": 0
    },
    {
      "period": "SO",
      "label": "SO",
      "home": 0,
      "away": 1
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
          "name": "Atlantic Division",
          "team": [
            {
              "position": "1",
              "name": "Ottawa Senators",
              "display_name": "Ottawa Senators",
              "games_played": "24",
              "won": "15",
              "lost": "6",
              "ot_losses": "3",
              "points": "33",
              "regular_ot_wins": "13",
              "shootout_wins": "2",
              "shootout_losses": "0",
              "home_record": "8-2-2",
              "road_record": "7-4-1",
              "goals_for": "79",
              "goals_against": "70",
              "difference": "+9",
              "last_ten": "7-1-2, 0 PTS",
              "streak": "W1",
              "code": "tt4x"
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
curl -s https://api.sportstatsapi.com/api/v1/coverage/hockey/l49f
```

## Runnable example: NHL results with OT and shootouts to CSV

[examples/nhl/results_ot_so_csv.py](../examples/nhl/results_ot_so_csv.py): Writes the finished games of a date range (default: the last 3 days, UTC) as CSV with one column that says how each game was decided: REG, OT or SO, plus the period scores. A summary line on stderr counts each kind. Python 3.8+, standard library only.

Run:

```bash
cd examples/nhl
export SSA_API_KEY=sk_live_your_key_here
python3 results_ot_so_csv.py --from 2026-11-20 --to 2026-11-22 > nhl-results.csv
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Links

- [NHL on SportStatsAPI](https://sportstatsapi.com/coverage/hockey/usa/nhl/): coverage, data and plans for this league
- [Free ice hockey API](https://sportstatsapi.com/developers/free-ice-hockey-api/)
- [Quickstart](https://sportstatsapi.com/docs/quickstart/): first request in a few minutes, and the [API reference](https://sportstatsapi.com/docs/api/)
- [Developer hub](https://sportstatsapi.com/developers/): free API pages per sport and an API comparison
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

[Data: SportStatsAPI](https://sportstatsapi.com/)
