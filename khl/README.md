# KHL API – free JSON examples (Python, JavaScript, curl)

Kontinental Hockey League games, final scores by period, overtime and shootout results, live scores and the standings as JSON, with the same request shape as the NHL. The league spans many time zones, so read `start_at` (UTC) and convert it to the time zone you show.

- League code: `l49c` (sport path `/hockey`)
- Free plan: the current season. Paid plans: every season we store (results from 2026-04-02, box scores from 2026-09-05, as reported by the public coverage endpoint on 2026-11-23).
- League page: [KHL data API on SportStatsAPI](https://sportstatsapi.com/coverage/hockey/russia/khl/)

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

Upcoming KHL matches between two dates (inclusive, UTC). Without dates the list covers today only.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches?league_id=l49c&date_from=2026-11-24&date_to=2026-11-26" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l49c", "date_from": "2026-11-24", "date_to": "2026-11-26"})
r.raise_for_status()
for m in r.json()["data"]:
    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l49c", date_from: "2026-11-24", date_to: "2026-11-26" });
const res = await fetch(`${BASE}/hockey/matches?${q}`, { headers });
const { data } = await res.json();
for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);
```

## Results

Finished matches, newest first. Keep the rows whose `status_code` starts with "final". `status_code` tells how a game ended: "final" (regulation), "final_overtime" or "final_penalties" (shootout). `periods` lists P1 to P3, then OT and SO when they were played. Take the final score from `home_team.score` and `away_team.score`: in a shootout game the SO entry may be the shootout tally, so the periods do not always add up to the final.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/matches?league_id=l49c&date_from=2026-11-20&date_to=2026-11-22&order=desc" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l49c", "date_from": "2026-11-20", "date_to": "2026-11-22", "order": "desc"})
for m in r.json()["data"]:
    if m["status_code"].startswith("final"):
        h, a = m["home_team"], m["away_team"]
        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l49c", date_from: "2026-11-20", date_to: "2026-11-22", order: "desc" });
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
live = [m for m in r.json()["data"] if m["league_code"] == "l49c"]
for m in live:
    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",
          m["away_team"]["score"], m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/hockey/matches/live`, { headers })).json();
const live = data.filter((m) => m.league_code === "l49c");
for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
```

## Standings

The current table in one request. The table is one list of groups: the two conferences first, then the four divisions, each with its teams. A row has position (`pos`), games played (`gp`), points (`pts`), the result columns `w`, `wo`, `l` and `lo`, goals in `points_for` and `points_against`, and a playoff note in `description`.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/hockey/leagues/l49c/standings" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/hockey/leagues/l49c/standings", headers=HEADERS, timeout=30)
table = r.json()["data"]
for group in table["standings"]["category"]["league"]:
    for row in group["team"]:
        print(group["name"], row["pos"], row["name"], row["pts"], "pts")
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/hockey/leagues/l49c/standings`, { headers })).json();
for (const group of data.standings.category.league) {
  for (const row of group.team) console.log(group.name, row.pos, row.name, row.pts, "pts");
}
```

## Real response, trimmed

One finished KHL match from `/hockey/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`.

JSON:

```json
{
  "code": "mo07p",
  "league_code": "l49c",
  "status": "After Penalties",
  "status_code": "final_penalties",
  "start_at": "2026-11-20T16:00:00Z",
  "home_team": {
    "code": "tt9z",
    "name": "Cherepovets",
    "score": 3
  },
  "away_team": {
    "code": "tt3c",
    "name": "Khabarovsk",
    "score": 2
  },
  "periods": [
    {
      "period": "1",
      "label": "P1",
      "home": 1,
      "away": 1
    },
    {
      "period": "2",
      "label": "P2",
      "home": 0,
      "away": 1
    },
    {
      "period": "3",
      "label": "P3",
      "home": 1,
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
      "home": 2,
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
      "name": "Western Conference",
      "team": [
        {
          "description": {
            "value": "Promotion - KHL (Play Offs: 1/8-finals)"
          },
          "gp": "29",
          "code": "tt2v",
          "l": "6",
          "lo": "2",
          "name": "CSKA Moscow",
          "display_name": "CSKA Moscow",
          "points_against": "53",
          "points_for": "94",
          "pos": "1",
          "pts": "44",
          "recent_form": "",
          "w": "18",
          "wo": "3"
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
curl -s https://api.sportstatsapi.com/api/v1/coverage/hockey/l49c
```

## Runnable example: KHL results with OT and shootouts to CSV

[examples/khl/results_ot_so_csv.py](../examples/khl/results_ot_so_csv.py): Writes the finished KHL games of a date range (default: the last 3 days, UTC) as CSV with how each game was decided (REG, OT or SO) and the period scores. It is the NHL script with another league code: change `LEAGUE` to use it for any hockey league. Python 3.8+, standard library only.

Run:

```bash
cd examples/khl
export SSA_API_KEY=sk_live_your_key_here
python3 results_ot_so_csv.py --from 2026-11-20 --to 2026-11-22 > khl-results.csv
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Links

- [KHL on SportStatsAPI](https://sportstatsapi.com/coverage/hockey/russia/khl/): coverage, data and plans for this league
- [Free ice hockey API](https://sportstatsapi.com/developers/free-ice-hockey-api/)
- [Quickstart](https://sportstatsapi.com/docs/quickstart/): first request in a few minutes, and the [API reference](https://sportstatsapi.com/docs/api/)
- [Developer hub](https://sportstatsapi.com/developers/): free API pages per sport and an API comparison
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

[Data: SportStatsAPI](https://sportstatsapi.com/)
