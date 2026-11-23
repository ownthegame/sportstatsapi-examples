"""Premier League table to CSV with the SportStatsAPI free plan.

    export SSA_API_KEY=sk_live_...     # free key: https://account.sportstatsapi.com/signup
    python3 table_to_csv.py > premier-league-table.csv

One request. Standard library only. Data: SportStatsAPI (https://sportstatsapi.com)
"""
import csv
import json
import os
import sys
import urllib.request

BASE = "https://api.sportstatsapi.com/api/v1"
LEAGUE = "l30"  # Premier League


def get(path: str) -> dict:
    key = os.environ.get("SSA_API_KEY") or sys.exit("Set SSA_API_KEY (free key: https://account.sportstatsapi.com/signup)")
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}",
                                                       "User-Agent": "sportstatsapi-examples/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # HTTPError 429 = over the Free limit, try later
        return json.load(r)


def main() -> None:
    data = get(f"/soccer/leagues/{LEAGUE}/standings")["data"]
    teams = data["standings"]["tournament"]["team"]
    out = csv.writer(sys.stdout)
    out.writerow(["pos", "team", "played", "won", "drawn", "lost", "gf", "ga", "gd", "points", "form"])
    for t in teams:
        o = t["overall"]
        out.writerow([t["@position"], t["@name"], o["@gp"], o["@w"], o["@d"], o["@l"], o["@gs"], o["@ga"],
                      t["total"]["@gd"], t["total"]["@p"], t.get("@recent_form", "")])
    print(f"{len(teams)} teams, season {data['season']}. Data: SportStatsAPI (https://sportstatsapi.com)", file=sys.stderr)


if __name__ == "__main__":
    main()
