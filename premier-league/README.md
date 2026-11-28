# Premier League API – free JSON examples (Python, JavaScript, curl)

Fixtures, results, live scores and the league table of the English Premier League as JSON. A match comes with its round ("Week 11"), venue, half-time and full-time score and the goals with the minute. Team names are plain strings, and every team and match has a short stable `code` you can store as your own key.

- League code: `l30` (sport path `/soccer`)
- Free plan: the current season. Paid plans: every season we store (results from 2016-08-13, box scores from 2026-04-10, as reported by the public coverage endpoint on 2026-11-23).
- League page: [Premier League data API on SportStatsAPI](https://sportstatsapi.com/coverage/soccer/england/premier-league/)

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

Upcoming Premier League matches between two dates (inclusive, UTC). Without dates the list covers today only.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/soccer/matches?league_id=l30&date_from=2026-11-28&date_to=2026-12-01" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/soccer/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l30", "date_from": "2026-11-28", "date_to": "2026-12-01"})
r.raise_for_status()
for m in r.json()["data"]:
    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l30", date_from: "2026-11-28", date_to: "2026-12-01" });
const res = await fetch(`${BASE}/soccer/matches?${q}`, { headers });
const { data } = await res.json();
for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);
```

## Results

Finished matches, newest first. Keep the rows whose `status_code` starts with "final". A finished league match has `status` "FT" and `status_code` "final". `periods` holds the first-half score and the full-time score (`cumulative: true` means it is the score after 90 minutes, not the goals of the second half).

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/soccer/matches?league_id=l30&date_from=2026-11-20&date_to=2026-11-23&order=desc" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/soccer/matches", headers=HEADERS, timeout=30,
                 params={"league_id": "l30", "date_from": "2026-11-20", "date_to": "2026-11-23", "order": "desc"})
for m in r.json()["data"]:
    if m["status_code"].startswith("final"):
        h, a = m["home_team"], m["away_team"]
        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const q = new URLSearchParams({ league_id: "l30", date_from: "2026-11-20", date_to: "2026-11-23", order: "desc" });
const { data } = await (await fetch(`${BASE}/soccer/matches?${q}`, { headers })).json();
for (const m of data.filter((m) => m.status_code.startsWith("final"))) {
  console.log(m.start_date, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
}
```

## Live scores

`/soccer/matches/live` returns every live football (soccer) match of all leagues in one list, so filter on `league_code`. On the Free plan live scores are up to 15 minutes behind; poll once a minute at most (5 requests a minute is the Free cap).

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/soccer/matches/live" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/soccer/matches/live", headers=HEADERS, timeout=30)
live = [m for m in r.json()["data"] if m["league_code"] == "l30"]
for m in live:
    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",
          m["away_team"]["score"], m["away_team"]["name"])
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/soccer/matches/live`, { headers })).json();
const live = data.filter((m) => m.league_code === "l30");
for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);
```

## Standings

The current table in one request. The table is one list. Each row keeps the feed's attribute style: keys start with `@`, numbers come as strings, and `overall`, `home`, `away` and `total` hold the records.

curl:

```bash
curl -s "https://api.sportstatsapi.com/api/v1/soccer/leagues/l30/standings" \
  -H "Authorization: Bearer $SSA_API_KEY"
```

Python:

```python
r = requests.get(f"{BASE}/soccer/leagues/l30/standings", headers=HEADERS, timeout=30)
table = r.json()["data"]
for row in table["standings"]["tournament"]["team"]:
    print(row["@position"], row["@name"], row["total"]["@p"], "pts")
```

JavaScript:

```javascript
const BASE = "https://api.sportstatsapi.com/api/v1";
const headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };
const { data } = await (await fetch(`${BASE}/soccer/leagues/l30/standings`, { headers })).json();
for (const row of data.standings.tournament.team) {
  console.log(row["@position"], row["@name"], row.total["@p"], "pts");
}
```

## Real response, trimmed

One finished Premier League match from `/soccer/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`.

JSON:

```json
{
  "code": "m907w",
  "league_code": "l30",
  "status": "FT",
  "status_code": "final",
  "start_at": "2026-11-22T16:30:00Z",
  "round": "Week 11",
  "home_team": {
    "code": "tll3",
    "name": "Liverpool",
    "score": 4
  },
  "away_team": {
    "code": "tllc",
    "name": "Manchester Utd",
    "score": 0
  },
  "periods": [
    {
      "period": "1",
      "label": "1st half",
      "home": 2,
      "away": 0
    },
    {
      "period": "FT",
      "label": "Full time",
      "home": 4,
      "away": 0,
      "cumulative": true
    }
  ],
  "half_time_score": "[2-0]",
  "full_time_score": "[4-0]"
}
```

And the first row of the standings (structure kept, other rows cut):

JSON:

```json
{
  "@position": "1",
  "@name": "Arsenal",
  "@recent_form": "DWWWW",
  "overall": {
    "@gp": "11",
    "@w": "9",
    "@d": "1",
    "@l": "1",
    "@gs": "17",
    "@ga": "7"
  },
  "total": {
    "@gd": "10",
    "@p": "28"
  }
}
```

## Paging and coverage

`limit` goes up to 100 (default 50); use `offset` and `meta.total` to page through longer lists. What a league has (live scores, box scores, play-by-play, history) is public, no key needed:

curl (no key):

```bash
curl -s https://api.sportstatsapi.com/api/v1/coverage/soccer/l30
```

## Runnable example: Premier League table to CSV

[examples/premier-league/table_to_csv.py](../examples/premier-league/table_to_csv.py): Reads the current table (one request) and writes position, team, played, won, drawn, lost, goals for and against, goal difference, points and recent form as CSV. Open it in a spreadsheet or load it with pandas. Python 3.8+, standard library only.

Run:

```bash
cd examples/premier-league
export SSA_API_KEY=sk_live_your_key_here
python3 table_to_csv.py > premier-league-table.csv
```

> **Free plan limits.** 100 requests a day for the whole account and 5 a minute, the current season of every league, data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "Data: SportStatsAPI" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan](https://sportstatsapi.com/pricing/) (from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute.

## Links

- [Premier League on SportStatsAPI](https://sportstatsapi.com/coverage/soccer/england/premier-league/): coverage, data and plans for this league
- [Free football (soccer) API](https://sportstatsapi.com/developers/free-football-api/)
- [Quickstart](https://sportstatsapi.com/docs/quickstart/): first request in a few minutes, and the [API reference](https://sportstatsapi.com/docs/api/)
- [Developer hub](https://sportstatsapi.com/developers/): free API pages per sport and an API comparison
- [Pricing](https://sportstatsapi.com/pricing/): Free, one sport, all sports
- [Free sign-up](https://account.sportstatsapi.com/signup)
- [FAQ](https://sportstatsapi.com/faq/) and [terms](https://sportstatsapi.com/legal/terms/): what Free allows
- [All covered competitions](https://sportstatsapi.com/coverage/)

[Data: SportStatsAPI](https://sportstatsapi.com/)
