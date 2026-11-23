"""One NFL week of final scores to a JSON file with the SportStatsAPI free plan.

    export SSA_API_KEY=sk_live_...     # free key: https://account.sportstatsapi.com/signup
    python3 week_scores_json.py --from 2026-11-19 --to 2026-11-24 --out week.json

Match answers have no week number: a week is a date range in UTC (Thursday to Tuesday
catches the Monday night game, which ends after midnight UTC).
Standard library only. Data: SportStatsAPI (https://sportstatsapi.com)
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://api.sportstatsapi.com/api/v1"
LEAGUE = "l53v"  # NFL


def get(path: str, **params) -> dict:
    key = os.environ.get("SSA_API_KEY") or sys.exit("Set SSA_API_KEY (free key: https://account.sportstatsapi.com/signup)")
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "sportstatsapi-examples/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # HTTPError 429 = over the Free limit, try later
        return json.load(r)


def main() -> None:
    today = dt.datetime.now(dt.timezone.utc).date()
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="date_from", default=str(today - dt.timedelta(days=7)))
    p.add_argument("--to", dest="date_to", default=str(today))
    p.add_argument("--out", default="week.json")
    a = p.parse_args()

    # one NFL week is at most 16 games: one page of 100 is enough
    data = get("/american-football/matches", league_id=LEAGUE, date_from=a.date_from, date_to=a.date_to, limit=100)["data"]
    games = [{
        "code": m["code"],
        "kickoff": m["start_at"],
        "home": m["home_team"]["name"],
        "away": m["away_team"]["name"],
        "score": [m["home_team"]["score"], m["away_team"]["score"]],
        "quarters": {x["label"]: [x["home"], x["away"]] for x in m["periods"]},
        "overtime": any(x["period"] == "OT" for x in m["periods"]),
    } for m in data if m["status_code"].startswith("final")]
    doc = {"from": a.date_from, "to": a.date_to, "games": games,
           "credit": "Data: SportStatsAPI (https://sportstatsapi.com)"}
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"{len(games)} finished games written to {a.out}. Data: SportStatsAPI (https://sportstatsapi.com)")


if __name__ == "__main__":
    main()
