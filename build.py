"""Build the GitHub Pages site (docs/) and the per-league README.md files from leagues.json.

Run: python3 build.py   (stdlib only; no network)
Add a league: append one entry to leagues.json, run the build, commit.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://ownthegame.github.io/sportstatsapi-examples/"
REPO = "https://github.com/ownthegame/sportstatsapi-examples"
API = "https://api.sportstatsapi.com/api/v1"
SSA = "https://sportstatsapi.com/"
DOCS = "https://sportstatsapi.com/docs/api/"
QUICKSTART = "https://sportstatsapi.com/docs/quickstart/"
PRICING = "https://sportstatsapi.com/pricing/"
SIGNUP = "https://account.sportstatsapi.com/signup"
FAQ = "https://sportstatsapi.com/faq/"
TERMS = "https://sportstatsapi.com/legal/terms/"
COVERAGE = "https://sportstatsapi.com/coverage/"
DEVELOPERS = "https://sportstatsapi.com/developers/"

FREE_TIP = (
    "100 requests a day for the whole account and 5 a minute, the current season of every league, "
    "data up to 15 minutes old (live scores too), non-commercial use only, with a visible credit line "
    "\"Data: SportStatsAPI\" linking to https://sportstatsapi.com. Over a limit the API answers HTTP 429. "
    f"Past seasons, line-ups, player stats, box scores, play-by-play and odds need a [paid plan]({PRICING}) "
    "(from $79 a month for one sport). Cache what you fetch: a table changes a few times a day, not every minute."
)


# ---------- tiny markup: blocks -> Markdown or HTML ----------
# A block is (kind, *args): ("h2", text), ("p", text), ("code", lang, label, text), ("tip", text), ("ul", [text, ...])
# Inline text understands `code` and [label](url).

def inline_html(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)


def slug_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def to_html(blocks: list) -> str:
    parts = []
    for kind, *a in blocks:
        if kind == "h2":
            parts.append(f'<h2 id="{slug_id(a[0])}">{inline_html(a[0])}</h2>')
        elif kind == "h3":
            parts.append(f"<h3>{inline_html(a[0])}</h3>")
        elif kind == "p":
            parts.append(f"<p>{inline_html(a[0])}</p>")
        elif kind == "ul":
            parts.append("<ul>" + "".join(f"<li>{inline_html(i)}</li>" for i in a[0]) + "</ul>")
        elif kind == "tip":
            parts.append(f'<aside class="tip"><strong>Free plan limits.</strong> {inline_html(a[0])}</aside>')
        elif kind == "code":
            lang, label, code = a
            parts.append(f'<figure class="code"><figcaption>{html.escape(label)}</figcaption>'
                         f'<pre><code class="language-{lang}">{html.escape(code)}</code></pre></figure>')
    return "\n".join(parts)


def to_md(blocks: list) -> str:
    parts = []
    for kind, *a in blocks:
        if kind == "h2":
            parts.append(f"## {a[0]}")
        elif kind == "h3":
            parts.append(f"### {a[0]}")
        elif kind == "p":
            parts.append(a[0])
        elif kind == "ul":
            parts.append("\n".join(f"- {i}" for i in a[0]))
        elif kind == "tip":
            parts.append(f"> **Free plan limits.** {a[0]}")
        elif kind == "code":
            lang, label, code = a
            parts.append(f"{label}:\n\n```{lang}\n{code}\n```")
    return "\n\n".join(parts) + "\n"


# ---------- page content ----------

def calls(lg: dict) -> list:
    s, c = lg["sport"], lg["code"]
    fa, fb = lg["fixtures_dates"]
    ra, rb = lg["results_dates"]
    auth = '-H "Authorization: Bearer $SSA_API_KEY"'
    js_head = 'const BASE = "https://api.sportstatsapi.com/api/v1";\nconst headers = { Authorization: `Bearer ${process.env.SSA_API_KEY}` };\n'
    return [
        ("Fixtures for a date range",
         f"Upcoming {lg['name']} matches between two dates (inclusive, UTC). Without dates the list covers today only.",
         f'curl -s "{API}/{s}/matches?league_id={c}&date_from={fa}&date_to={fb}" \\\n  {auth}',
         f'r = requests.get(f"{{BASE}}/{s}/matches", headers=HEADERS, timeout=30,\n'
         f'                 params={{"league_id": "{c}", "date_from": "{fa}", "date_to": "{fb}"}})\n'
         f'r.raise_for_status()\nfor m in r.json()["data"]:\n'
         f'    print(m["start_at"], m["home_team"]["name"], "vs", m["away_team"]["name"])',
         f'{js_head}const q = new URLSearchParams({{ league_id: "{c}", date_from: "{fa}", date_to: "{fb}" }});\n'
         f'const res = await fetch(`${{BASE}}/{s}/matches?${{q}}`, {{ headers }});\n'
         f'const {{ data }} = await res.json();\n'
         f'for (const m of data) console.log(m.start_at, m.home_team.name, "vs", m.away_team.name);'),
        ("Results",
         f"Finished matches, newest first. Keep the rows whose `status_code` starts with \"final\". {lg['results_note']}",
         f'curl -s "{API}/{s}/matches?league_id={c}&date_from={ra}&date_to={rb}&order=desc" \\\n  {auth}',
         f'r = requests.get(f"{{BASE}}/{s}/matches", headers=HEADERS, timeout=30,\n'
         f'                 params={{"league_id": "{c}", "date_from": "{ra}", "date_to": "{rb}", "order": "desc"}})\n'
         f'for m in r.json()["data"]:\n    if m["status_code"].startswith("final"):\n'
         f'        h, a = m["home_team"], m["away_team"]\n'
         f'        print(m["start_date"], h["name"], h["score"], "-", a["score"], a["name"], m["status_code"])',
         f'{js_head}const q = new URLSearchParams({{ league_id: "{c}", date_from: "{ra}", date_to: "{rb}", order: "desc" }});\n'
         f'const {{ data }} = await (await fetch(`${{BASE}}/{s}/matches?${{q}}`, {{ headers }})).json();\n'
         f'for (const m of data.filter((m) => m.status_code.startsWith("final"))) {{\n'
         f'  console.log(m.start_date, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);\n}}'),
        ("Live scores",
         f"`/{s}/matches/live` returns every live {lg['sport_label']} match of all leagues in one list, so filter on `league_code`. "
         "On the Free plan live scores are up to 15 minutes behind; poll once a minute at most (5 requests a minute is the Free cap).",
         f'curl -s "{API}/{s}/matches/live" \\\n  {auth}',
         f'r = requests.get(f"{{BASE}}/{s}/matches/live", headers=HEADERS, timeout=30)\n'
         f'live = [m for m in r.json()["data"] if m["league_code"] == "{c}"]\n'
         f'for m in live:\n    print(m["status"], m["home_team"]["name"], m["home_team"]["score"], "-",\n'
         f'          m["away_team"]["score"], m["away_team"]["name"])',
         f'{js_head}const {{ data }} = await (await fetch(`${{BASE}}/{s}/matches/live`, {{ headers }})).json();\n'
         f'const live = data.filter((m) => m.league_code === "{c}");\n'
         f'for (const m of live) console.log(m.status, m.home_team.name, m.home_team.score, "-", m.away_team.score, m.away_team.name);'),
        ("Standings",
         f"The current table in one request. {lg['standings_intro']}",
         f'curl -s "{API}/{s}/leagues/{c}/standings" \\\n  {auth}',
         f'r = requests.get(f"{{BASE}}/{s}/leagues/{c}/standings", headers=HEADERS, timeout=30)\n'
         f'table = r.json()["data"]\n{lg["standings_py"]}',
         f'{js_head}const {{ data }} = await (await fetch(`${{BASE}}/{s}/leagues/{c}/standings`, {{ headers }})).json();\n'
         f'{lg["standings_js"]}'),
    ]


def history_line(cov: dict) -> str:
    h = cov["history"]
    bits = [f"results from {h['results_from']}"]
    if h.get("box_scores_from"):
        bits.append(f"box scores from {h['box_scores_from']}")
    if h.get("play_by_play_from"):
        bits.append(f"play-by-play from {h['play_by_play_from']}")
    return ", ".join(bits)


def league_blocks(lg: dict, md: bool) -> list:
    s, c = lg["sport"], lg["code"]
    script = lg.get("script")
    script_path = f"examples/{lg['slug']}/{script['file']}" if script else ""
    script_link = (f"../{script_path}" if md else f"{REPO}/blob/main/{script_path}") if script else ""
    b = [
        ("p", lg["intro"]),
        ("ul", [
            f"League code: `{c}` (sport path `/{s}`)",
            f"Free plan: the current season. Paid plans: every season we store ({history_line(lg['coverage'])}, as reported by the public coverage endpoint on {lg['coverage']['checked']}).",
            f"League page: [{lg['name']} data API on SportStatsAPI]({lg['ssa_url']})",
        ]),
        ("h2", "Setup"),
        ("p", f"[Sign up free]({SIGNUP}) (confirm the e-mail link), copy your key once, and keep it out of your code: put it in an environment variable. Call the API from a server or script, never from browser code, where anyone can read the key."),
        ("code", "bash", "Shell", "export SSA_API_KEY=sk_live_your_key_here"),
        ("code", "python", "Python setup used below (pip install requests)",
         'import os\nimport requests\n\nBASE = "https://api.sportstatsapi.com/api/v1"\nHEADERS = {"Authorization": f"Bearer {os.environ[\'SSA_API_KEY\']}"}'),
        ("p", "The JavaScript snippets use the built-in `fetch` of Node 18+; save them as `.mjs` files so top-level `await` works."),
    ]
    for title, text, curl, py, js in calls(lg):
        b += [("h2", title), ("p", text),
              ("code", "bash", "curl", curl), ("code", "python", "Python", py), ("code", "javascript", "JavaScript", js)]
    b += [
        ("h2", "Real response, trimmed"),
        ("p", f"One finished {lg['name']} match from `/{s}/matches` (fetched on the Free plan, most fields cut). Every answer wraps the result in `data`; lists also carry `meta.total`, `meta.limit` and `meta.offset`."),
        ("code", "json", "JSON", json.dumps(lg["sample_match"], indent=2, ensure_ascii=False)),
        ("p", "And the first row of the standings (structure kept, other rows cut):"),
        ("code", "json", "JSON", json.dumps(lg["sample_standings"], indent=2, ensure_ascii=False)),
        ("h2", "Paging and coverage"),
        ("p", "`limit` goes up to 100 (default 50); use `offset` and `meta.total` to page through longer lists. "
              "What a league has (live scores, box scores, play-by-play, history) is public, no key needed:"),
        ("code", "bash", "curl (no key)", f"curl -s {API}/coverage/{s}/{c}"),
    ]
    if script:
        b += [
            ("h2", f"Runnable example: {script['title']}"),
            ("p", f"[{script_path}]({script_link}): {script['about']} Python 3.8+, standard library only."),
            ("code", "bash", "Run", f"cd examples/{lg['slug']}\nexport SSA_API_KEY=sk_live_your_key_here\n{script['run']}"),
        ]
    b += [("tip", FREE_TIP), ("h2", "Links"), ("ul", links_list(lg))]
    return b


def links_list(lg: dict | None = None) -> list:
    items = []
    if lg:
        items.append(f"[{lg['name']} on SportStatsAPI]({lg['ssa_url']}): coverage, data and plans for this league")
        items.append(f"[Free {lg['sport_label']} API]({lg['sport_url']})")
    items += [
        f"[Quickstart]({QUICKSTART}): first request in a few minutes, and the [API reference]({DOCS})",
        f"[Developer hub]({DEVELOPERS}): free API pages per sport and an API comparison",
        f"[Pricing]({PRICING}): Free, one sport, all sports",
        f"[Free sign-up]({SIGNUP})",
        f"[FAQ]({FAQ}) and [terms]({TERMS}): what Free allows",
        f"[All covered competitions]({COVERAGE})",
    ]
    return items


def index_blocks(leagues: list, md: bool) -> list:
    rows = []
    for lg in leagues:
        page = f"{lg['slug']}/README.md" if md else f"{lg['slug']}/"
        rows.append(f"[{lg['name']} API examples]({page}): {lg['sport_label']}, {lg['country']}, league code `{lg['code']}`"
                    + (f", script: {lg['script']['title']}" if lg.get("script") else ""))
    return [
        ("p", f"Copy-paste code for the [SportStatsAPI]({SSA}) sports data API: fixtures, results, live scores and standings "
              "for popular leagues in curl, Python and JavaScript, plus one small runnable script per league. "
              "All examples work with a free key."),
        ("h2", "Leagues"),
        ("ul", rows),
        ("h2", "Quick start"),
        ("ul", [
            f"[Create a free account]({SIGNUP}) and confirm the e-mail link. Your key starts with `sk_live_` and is shown once.",
            "Put it in an environment variable: `export SSA_API_KEY=sk_live_...`",
            "Send it as a bearer token. Every call is a GET under `https://api.sportstatsapi.com/api/v1`.",
        ]),
        ("code", "bash", "curl: today's live hockey scores", f'curl -s "{API}/hockey/matches/live" \\\n  -H "Authorization: Bearer $SSA_API_KEY"'),
        ("p", "Find any league's code without a key: `/coverage/{sport}/{league}` takes our code or the competition key."),
        ("code", "bash", "curl (no key)", f"curl -s {API}/coverage/soccer/england--premier-league"),
        ("p", "Then run a script, for example the Premier League table to CSV:"),
        ("code", "bash", "Run", "git clone https://github.com/ownthegame/sportstatsapi-examples\ncd sportstatsapi-examples/examples/premier-league\npython3 table_to_csv.py > table.csv"),
        ("tip", FREE_TIP),
        ("h2", "Add a league"),
        ("p", "Every page is generated from one entry in `leagues.json` (league code, sport, dates for the examples, a trimmed real response). "
              "Add an entry, run `python3 build.py`, and the page, its README and the sitemap are written."),
        ("h2", "Links"),
        ("ul", links_list()),
        ("p", "Code in this repository is MIT licensed. The API data is not: it is used under the SportStatsAPI [terms](" + TERMS + ")."),
    ]


# ---------- HTML shell ----------

def page(title: str, desc: str, url: str, body: str, css: str, crumbs: str) -> str:
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="--YC6oyD16P7J92EvIpuj-CJdCvzZuZTfFQwmcQNudo">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="SportStatsAPI examples">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="top"><nav>{crumbs}<span class="sp"></span><a href="{DOCS}">API docs</a><a href="{PRICING}">Pricing</a><a class="btn" href="{SIGNUP}">Get a free key</a></nav></header>
<main>
<h1>{t}</h1>
{body}
</main>
<footer><p><a href="{SSA}">Data: SportStatsAPI</a> · Code MIT licensed · <a href="{REPO}">Source on GitHub</a></p></footer>
</body>
</html>
"""


def md_page(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n[Data: SportStatsAPI]({SSA})\n"


def main() -> None:
    leagues = json.loads((ROOT / "leagues.json").read_text())
    css_root, docs = "style.css", ROOT / "docs"
    urls = [SITE]
    for lg in leagues:
        title = f"{lg['name']} API – free JSON examples (Python, JavaScript, curl)"
        desc = (f"{lg['name']} ({lg['country']}) API examples: fixtures, results, live scores and standings as JSON "
                f"with curl, Python and JavaScript, league code {lg['code']}, plus a runnable script. Free key.")
        url = f"{SITE}{lg['slug']}/"
        urls.append(url)
        crumbs = f'<a href="../">SportStatsAPI examples</a><span>/</span><span>{html.escape(lg["name"])}</span>'
        out = docs / lg["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(title, desc, url, to_html(league_blocks(lg, md=False)), "../" + css_root, crumbs))
        (ROOT / lg["slug"]).mkdir(exist_ok=True)
        (ROOT / lg["slug"] / "README.md").write_text(md_page(title, to_md(league_blocks(lg, md=True))))

    title = "SportStatsAPI examples – sports data API code for Python, JavaScript and curl"
    desc = ("Free code examples for a sports data API: Premier League, NBA, NFL, NHL and KHL fixtures, results, "
            "live scores and standings as JSON in curl, Python and JavaScript.")
    (docs / "index.html").write_text(page(title, desc, SITE, to_html(index_blocks(leagues, md=False)), css_root,
                                          '<a href="./">SportStatsAPI examples</a>'))
    (ROOT / "README.md").write_text(md_page(title, to_md(index_blocks(leagues, md=True))))

    sm = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
    (docs / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                                      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    (docs / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    print(f"built {len(leagues)} league pages")


if __name__ == "__main__":
    main()
