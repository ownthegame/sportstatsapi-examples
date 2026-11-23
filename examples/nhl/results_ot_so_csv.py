"""NHL results with overtime and shootouts to CSV with the SportStatsAPI free plan.

    export SSA_API_KEY=sk_live_...     # free key: https://account.sportstatsapi.com/signup
    python3 results_ot_so_csv.py --from 2026-11-20 --to 2026-11-22 > nhl-results.csv

Change LEAGUE to use it for another hockey league (KHL is l49c).
Standard library only. Data: SportStatsAPI (https://sportstatsapi.com)
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://api.sportstatsapi.com/api/v1"
LEAGUE = "l49f"  # NHL
DECIDED = {"final": "REG", "final_overtime": "OT", "final_penalties": "SO"}


def get(path: str, **params) -> dict:
    key = os.environ.get("SSA_API_KEY") or sys.exit("Set SSA_API_KEY (free key: https://account.sportstatsapi.com/signup)")
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "sportstatsapi-examples/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # HTTPError 429 = over the Free limit, try later
        return json.load(r)


def main() -> None:
    today = dt.datetime.now(dt.timezone.utc).date()
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="date_from", default=str(today - dt.timedelta(days=3)))
    p.add_argument("--to", dest="date_to", default=str(today))
    a = p.parse_args()

    games, offset = [], 0
    while True:
        page = get("/hockey/matches", league_id=LEAGUE, date_from=a.date_from, date_to=a.date_to, limit=100, offset=offset)
        games += [m for m in page["data"] if m["status_code"] in DECIDED]
        offset += len(page["data"])
        if not page["data"] or offset >= page["meta"]["total"]:
            break

    out = csv.writer(sys.stdout)
    out.writerow(["date", "home", "away", "home_score", "away_score", "decided", "periods"])
    for m in games:
        periods = " ".join(f"{x['label']}:{x['home']}-{x['away']}" for x in m["periods"])
        out.writerow([m["start_date"], m["home_team"]["name"], m["away_team"]["name"],
                      m["home_team"]["score"], m["away_team"]["score"], DECIDED[m["status_code"]], periods])
    count = collections.Counter(DECIDED[m["status_code"]] for m in games)
    print(f"{len(games)} games: {count['REG']} regulation, {count['OT']} overtime, {count['SO']} shootout. "
          "Data: SportStatsAPI (https://sportstatsapi.com)", file=sys.stderr)


if __name__ == "__main__":
    main()
