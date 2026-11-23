"""NBA results into a local SQLite file with the SportStatsAPI free plan.

    export SSA_API_KEY=sk_live_...     # free key: https://account.sportstatsapi.com/signup
    python3 results_to_sqlite.py --from 2026-11-20 --to 2026-11-23 --db nba.sqlite

Upserts by match code, so running it again never duplicates a game.
Standard library only. Data: SportStatsAPI (https://sportstatsapi.com)
"""
import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request

BASE = "https://api.sportstatsapi.com/api/v1"
LEAGUE = "l1jy"  # NBA


def get(path: str, **params) -> dict:
    key = os.environ.get("SSA_API_KEY") or sys.exit("Set SSA_API_KEY (free key: https://account.sportstatsapi.com/signup)")
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "sportstatsapi-examples/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # HTTPError 429 = over the Free limit, try later
        return json.load(r)


def finished_games(date_from: str, date_to: str) -> list:
    games, offset = [], 0
    while True:  # pages of 100; a few NBA days fit in one
        page = get("/basketball/matches", league_id=LEAGUE, date_from=date_from, date_to=date_to, limit=100, offset=offset)
        games += [m for m in page["data"] if m["status_code"].startswith("final")]
        offset += len(page["data"])
        if not page["data"] or offset >= page["meta"]["total"]:
            return games


def main() -> None:
    today = dt.datetime.now(dt.timezone.utc).date()
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="date_from", default=str(today - dt.timedelta(days=3)))
    p.add_argument("--to", dest="date_to", default=str(today))
    p.add_argument("--db", default="nba.sqlite")
    a = p.parse_args()

    db = sqlite3.connect(a.db)
    db.execute("""CREATE TABLE IF NOT EXISTS games (
        code TEXT PRIMARY KEY, start_at TEXT, home TEXT, away TEXT,
        home_score INTEGER, away_score INTEGER, status_code TEXT, periods TEXT)""")
    games = finished_games(a.date_from, a.date_to)
    with db:
        db.executemany("INSERT OR REPLACE INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
            (m["code"], m["start_at"], m["home_team"]["name"], m["away_team"]["name"],
             m["home_team"]["score"], m["away_team"]["score"], m["status_code"], json.dumps(m["periods"]))
            for m in games])
    total = db.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    print(f"{len(games)} finished games saved, {total} in {a.db}. Data: SportStatsAPI (https://sportstatsapi.com)")
    for row in db.execute("SELECT start_at, home, home_score, away_score, away FROM games ORDER BY start_at DESC LIMIT 5"):
        print(*row)


if __name__ == "__main__":
    main()
