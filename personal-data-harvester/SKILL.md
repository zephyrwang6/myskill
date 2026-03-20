---
name: personal-data-harvester
description: |
  Autonomously collect and structure a user's personal content history from Chinese and international platforms
  (豆瓣, 小红书, B站, 微信读书, 抖音, Kindle, etc.) using browser automation, local file parsing, and system
  share-sheet intake. Use this skill whenever the user wants to: build a personal knowledge base from their
  consumption history, sync reading/watching/collecting records into a local database, set up an automated
  pipeline to continuously harvest their data from social or reading platforms, or feed their content history
  into an AI agent for analysis. Trigger even if the user just says "帮我把豆瓣数据导进来", "同步我的读书记录",
  or "抓取我收藏的内容" — any phrase implying cross-platform personal data ingestion should use this skill.
compatibility:
  tools: [bash, computer]
  dependencies:
    - python3 (>=3.10)
    - playwright (pip install playwright && playwright install chromium)
    - sqlite3 (stdlib)
    - requests, beautifulsoup4, pydantic (pip install ...)
---

# Personal Data Harvester

Helps Claude autonomously build and maintain a local pipeline that collects a user's personal content
history across platforms, stores it in a structured SQLite database, and keeps it fresh over time.

## Core philosophy

- **User's own data, user's own device.** All collection happens under the user's authenticated session
  or from locally cached files. Never store credentials; reuse existing browser sessions.
- **Graceful degradation.** Each platform has a primary and fallback strategy. If automation breaks
  (platform redesign, rate-limit), fall back to file import without losing prior data.
- **Privacy-first.** Data stays local by default. No uploads unless the user explicitly requests it.

---

## Step 0 — Assess the environment

Before writing any code, run this checklist:

```bash
python3 --version          # need >= 3.10
pip show playwright        # if missing: pip install playwright && playwright install chromium
pip show beautifulsoup4    # if missing: pip install beautifulsoup4 requests pydantic
ls ~/Library/Application\ Support/微信读书/ 2>/dev/null || echo "no local wechat-read cache"
```

Ask the user:
1. Which platforms to harvest first (prioritise by what they use most)?
2. Desktop or mobile primary device?
3. Acceptable harvest frequency (daily cron, manual trigger, or always-on daemon)?

Read `references/platforms.md` for per-platform technical details before writing any scraper.

---

## Step 1 — Initialise the local database

Always create this schema first. All scrapers write to the same DB.

```python
# scripts/init_db.py
import sqlite3, pathlib

DB = pathlib.Path.home() / ".personal-harvest" / "data.db"
DB.parent.mkdir(exist_ok=True)

with sqlite3.connect(DB) as con:
    con.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        id          TEXT PRIMARY KEY,          -- platform:platform_id
        platform    TEXT NOT NULL,             -- douban | bilibili | xiaohongshu | wechatread | kindle
        type        TEXT NOT NULL,             -- book | video | note | article | post
        title       TEXT,
        url         TEXT,
        creator     TEXT,
        tags        TEXT,                      -- JSON array
        user_rating INTEGER,                   -- 1-5 or null
        user_status TEXT,                      -- want | doing | done | liked | saved
        user_note   TEXT,                      -- user's own annotation
        summary     TEXT,                      -- AI-generated or platform description
        collected_at TEXT,                     -- ISO8601
        harvested_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_platform ON items(platform);
    CREATE INDEX IF NOT EXISTS idx_type     ON items(type);
    CREATE INDEX IF NOT EXISTS idx_status   ON items(user_status);
    """)
print(f"DB ready at {DB}")
```

---

## Step 2 — Choose collection strategy per platform

| Platform | Primary strategy | Fallback |
|---|---|---|
| 豆瓣 | Playwright browser automation (logged-in session) | HTML export + parse |
| 小红书 | Browser plugin DOM capture / Playwright | Manual share-sheet link intake |
| B 站 | Playwright (favorites API endpoint visible in DevTools) | Official data export |
| 微信读书 | Local SQLite cache file | Playwright web version |
| 抖音 | iOS/Android share-sheet → link resolver | Playwright (harder, rate-limited) |
| Kindle | `My Clippings.txt` file parse | Goodreads export |
| 豆瓣读书 App | Playwright web douban.com | Official "我的豆瓣"数据导出 |

See `references/platforms.md` for exact file paths, API endpoints, and selector patterns.

---

## Step 3 — Implement scrapers

### Pattern A — Playwright browser automation (豆瓣, B站, 小红书)

```python
# scripts/scrape_douban.py
"""
Collect 豆瓣 读过/在读/想读 books and watched films.
Requires: user already logged in to douban.com in the system Chromium profile.
"""
import asyncio, json, sqlite3, pathlib
from datetime import datetime
from playwright.async_api import async_playwright

DB = pathlib.Path.home() / ".personal-harvest" / "data.db"
DOUBAN_USER_ID = "YOUR_USER_ID"  # ask the user to provide or auto-detect from profile page

STATUSES = {
    "wish":    ("want",  f"https://book.douban.com/people/{DOUBAN_USER_ID}/wish"),
    "do":      ("doing", f"https://book.douban.com/people/{DOUBAN_USER_ID}/do"),
    "collect": ("done",  f"https://book.douban.com/people/{DOUBAN_USER_ID}/collect"),
}

async def scrape():
    async with async_playwright() as pw:
        # Connect to user's existing browser profile to reuse login session
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir=str(pathlib.Path.home() / ".config" / "personal-harvest-browser"),
            headless=False,   # show browser so user can log in first time
            slow_mo=800,      # human-like pacing to avoid rate limits
        )
        page = await browser.new_page()

        items = []
        for status_key, (status_label, url) in STATUSES.items():
            page_num = 1
            while True:
                await page.goto(f"{url}?start={(page_num-1)*15}&sort=time", wait_until="networkidle")
                await page.wait_for_timeout(1200)

                cards = await page.query_selector_all(".subject-item")
                if not cards:
                    break

                for card in cards:
                    title_el = await card.query_selector("h2 a")
                    title    = await title_el.inner_text() if title_el else ""
                    href     = await title_el.get_attribute("href") if title_el else ""
                    item_id  = href.split("/subject/")[-1].strip("/") if href else ""

                    rating_el = await card.query_selector(".rating")
                    rating_cls = await rating_el.get_attribute("class") if rating_el else ""
                    # class like "rating1-t" → 1 star, extract digit
                    rating = next((int(c[-3]) for c in rating_cls.split() if c.startswith("rating") and len(c) > 7), None)

                    note_el = await card.query_selector(".comment")
                    note    = (await note_el.inner_text()).strip() if note_el else None

                    date_el = await card.query_selector(".date")
                    date    = (await date_el.inner_text()).strip() if date_el else None

                    items.append({
                        "id": f"douban:{item_id}",
                        "platform": "douban",
                        "type": "book",
                        "title": title.strip(),
                        "url": href,
                        "user_status": status_label,
                        "user_rating": rating,
                        "user_note": note,
                        "collected_at": date,
                    })

                # check for next page
                next_btn = await page.query_selector("link[rel=next]")
                if not next_btn:
                    break
                page_num += 1

        # Upsert into DB
        with sqlite3.connect(DB) as con:
            con.executemany("""
                INSERT INTO items (id, platform, type, title, url, user_status, user_rating, user_note, collected_at)
                VALUES (:id, :platform, :type, :title, :url, :user_status, :user_rating, :user_note, :collected_at)
                ON CONFLICT(id) DO UPDATE SET
                    user_status  = excluded.user_status,
                    user_rating  = excluded.user_rating,
                    user_note    = excluded.user_note,
                    harvested_at = datetime('now')
            """, items)
        print(f"豆瓣: upserted {len(items)} items")
        await browser.close()

asyncio.run(scrape())
```

> **Agent instruction:** After writing the scraper, run it once in non-headless mode so the user can
> log in. Detect login success by checking for profile avatar element. Then re-run headless.

### Pattern B — Local file parse (微信读书, Kindle)

```python
# scripts/parse_wechatread.py
"""
Parse 微信读书 local SQLite cache on macOS.
Path: ~/Library/Containers/com.tencent.WeReadMac/Data/Library/Application Support/WeRead/
"""
import sqlite3, pathlib, json

WREAD_DB_GLOB = pathlib.Path.home().glob(
    "Library/Containers/com.tencent.WeReadMac/Data/Library/Application Support/WeRead/*.db"
)
HARVEST_DB = pathlib.Path.home() / ".personal-harvest" / "data.db"

def parse():
    items = []
    for src in WREAD_DB_GLOB:
        try:
            with sqlite3.connect(f"file:{src}?mode=ro", uri=True) as con:
                # Table names vary by version — discover them first
                tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                print(f"Tables in {src.name}: {tables}")

                # Common table: ZBOOK or book_info
                book_table = next((t for t in tables if "book" in t.lower()), None)
                if not book_table:
                    continue

                cols = [r[1] for r in con.execute(f"PRAGMA table_info({book_table})")]
                print(f"Columns: {cols}")

                rows = con.execute(f"SELECT * FROM {book_table} LIMIT 500").fetchall()
                for row in rows:
                    r = dict(zip(cols, row))
                    items.append({
                        "id": f"wechatread:{r.get('bookId', r.get('ZBOOKID', ''))}",
                        "platform": "wechatread",
                        "type": "book",
                        "title": r.get("title", r.get("ZTITLE", "")),
                        "creator": r.get("author", r.get("ZAUTHOR", "")),
                        "user_status": "doing" if r.get("readingProgress", 0) < 95 else "done",
                    })
        except Exception as e:
            print(f"Skipping {src.name}: {e}")

    with sqlite3.connect(HARVEST_DB) as con:
        con.executemany("""
            INSERT INTO items (id, platform, type, title, creator, user_status)
            VALUES (:id, :platform, :type, :title, :creator, :user_status)
            ON CONFLICT(id) DO NOTHING
        """, items)
    print(f"微信读书: inserted {len(items)} items")

parse()
```

```python
# scripts/parse_kindle.py
"""Parse Kindle My Clippings.txt for highlights and notes."""
import re, sqlite3, pathlib

CLIPPINGS = pathlib.Path.home() / "Documents" / "My Clippings.txt"
HARVEST_DB = pathlib.Path.home() / ".personal-harvest" / "data.db"

SEPARATOR = "=========="

def parse():
    if not CLIPPINGS.exists():
        print(f"Not found: {CLIPPINGS}"); return

    text = CLIPPINGS.read_text(encoding="utf-8-sig", errors="replace")
    entries = text.split(SEPARATOR)
    items, notes = {}, []

    for entry in entries:
        lines = [l.strip() for l in entry.strip().splitlines() if l.strip()]
        if len(lines) < 3: continue
        title_author = lines[0]
        content = "\n".join(lines[2:])

        book_id = re.sub(r"[^a-z0-9]", "", title_author.lower())[:40]
        item_id = f"kindle:{book_id}"
        if item_id not in items:
            m = re.match(r"^(.+?)\s*[\(\（](.+?)[\)\）]$", title_author)
            items[item_id] = {
                "id": item_id, "platform": "kindle", "type": "book",
                "title": m.group(1).strip() if m else title_author,
                "creator": m.group(2).strip() if m else None,
                "user_status": "done",
            }
        notes.append({"item_id": item_id, "note": content})

    with sqlite3.connect(HARVEST_DB) as con:
        con.executemany("""
            INSERT INTO items (id, platform, type, title, creator, user_status)
            VALUES (:id, :platform, :type, :title, :creator, :user_status)
            ON CONFLICT(id) DO NOTHING
        """, items.values())
    print(f"Kindle: {len(items)} books, {len(notes)} highlights")

parse()
```

---

## Step 4 — Self-healing: detect and fix breakage

After each run, check for anomalies:

```python
# scripts/health_check.py
import sqlite3, pathlib, json
from datetime import datetime, timedelta

DB = pathlib.Path.home() / ".personal-harvest" / "data.db"

with sqlite3.connect(DB) as con:
    report = {}
    for platform in ["douban", "bilibili", "wechatread", "kindle", "xiaohongshu"]:
        count = con.execute("SELECT COUNT(*) FROM items WHERE platform=?", (platform,)).fetchone()[0]
        last  = con.execute("SELECT MAX(harvested_at) FROM items WHERE platform=?", (platform,)).fetchone()[0]
        report[platform] = {"count": count, "last_harvested": last}

    total = con.execute("SELECT COUNT(*) FROM items").fetchone()[0]

print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"\nTotal items: {total}")

# Flag platforms not updated in 48h
for platform, info in report.items():
    if info["last_harvested"]:
        last_dt = datetime.fromisoformat(info["last_harvested"])
        if datetime.now() - last_dt > timedelta(hours=48):
            print(f"⚠️  {platform} stale — last harvest {info['last_harvested']}")
```

**When a scraper fails:**
1. Run health_check.py to identify which platform is stale
2. Inspect the live page: `await page.screenshot(path="debug.png")` to see current DOM
3. Update selectors in the scraper based on the screenshot
4. Re-run and verify count increases

---

## Step 5 — Set up continuous harvest (cron)

```bash
# Add to crontab: crontab -e
# Run all harvesters at 3am daily
0 3 * * * cd ~/.personal-harvest && python3 scripts/scrape_douban.py >> logs/douban.log 2>&1
0 3 * * * cd ~/.personal-harvest && python3 scripts/parse_wechatread.py >> logs/wechatread.log 2>&1
0 3 * * * cd ~/.personal-harvest && python3 scripts/health_check.py >> logs/health.log 2>&1
```

Or generate a launchd plist for macOS:

```xml
<!-- ~/Library/LaunchAgents/com.personal-harvest.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.personal-harvest</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/YOU/.personal-harvest/scripts/run_all.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/Users/YOU/.personal-harvest/logs/harvest.log</string>
</dict></plist>
```

---

## Step 6 — Expose data to agent

Once data is in SQLite, any downstream agent can query it:

```python
# Example: feed today's harvest summary to an AI agent
import sqlite3, pathlib

DB = pathlib.Path.home() / ".personal-harvest" / "data.db"

def get_recent_items(days=7, limit=50):
    with sqlite3.connect(DB) as con:
        rows = con.execute("""
            SELECT platform, type, title, creator, user_status, user_note, collected_at
            FROM items
            WHERE harvested_at >= datetime('now', '-? days')
            ORDER BY harvested_at DESC
            LIMIT ?
        """, (days, limit)).fetchall()
    return [dict(zip(["platform","type","title","creator","status","note","date"], r)) for r in rows]

def get_interest_profile():
    """Return aggregated interest signals for agent context."""
    with sqlite3.connect(DB) as con:
        by_status = dict(con.execute(
            "SELECT user_status, COUNT(*) FROM items GROUP BY user_status"
        ).fetchall())
        top_creators = [r[0] for r in con.execute(
            "SELECT creator, COUNT(*) c FROM items WHERE creator IS NOT NULL GROUP BY creator ORDER BY c DESC LIMIT 20"
        ).fetchall()]
    return {"counts_by_status": by_status, "top_creators": top_creators}
```

---

## Error patterns and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `TimeoutError` on page load | Platform slow / blocked | Increase `wait_until` timeout; add random delay |
| 0 cards returned | Selector changed after redesign | Screenshot page, update selector |
| Login redirect loop | Session expired | Re-launch non-headless, let user log in |
| DB locked | Two scrapers running at once | Add `timeout=30` to `sqlite3.connect()` |
| 微信读书 DB not found | Different macOS version path | Use glob pattern, print all found paths |
| Kindle clippings empty | Wrong mount path | Ask user to locate `My Clippings.txt` manually |

---

## References

- `references/platforms.md` — Per-platform: exact selectors, API endpoints, local file paths, rate limits
- `references/anti-detection.md` — Techniques to avoid bot detection (user-agent rotation, timing jitter, viewport randomisation)
