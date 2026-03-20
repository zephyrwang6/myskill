# Platform Technical Reference

Per-platform details for scrapers. Claude should read the relevant section before writing any scraper.

---

## 豆瓣 (Douban)

**Strategy:** Playwright, persistent browser context (reuse login session)

**Key URLs:**
```
书单: https://book.douban.com/people/{uid}/collect   # 读过
      https://book.douban.com/people/{uid}/wish      # 想读
      https://book.douban.com/people/{uid}/do        # 在读
影单: https://movie.douban.com/people/{uid}/collect
      https://movie.douban.com/people/{uid}/wish
```

**Auto-detect UID:**
```python
await page.goto("https://www.douban.com/mine/")
url = page.url   # redirects to https://www.douban.com/people/{uid}/
uid = url.split("/people/")[-1].strip("/")
```

**Selectors (as of 2025):**
```python
cards       = ".subject-item"
title_link  = "h2 a"           # href contains /subject/{id}/
rating      = ".rating"         # class="rating3-t" → 3 stars
date        = ".date"
comment     = ".comment"
next_page   = "link[rel=next]"
```

**Pagination:** `?start=0&15&30...` (15 per page). Stop when 0 cards returned.

**Rate limit:** 1 request per 1–2s with random jitter. Douban tolerates ~200 req/session before
showing captcha. If captcha appears: pause 10min, then resume.

**Data export alternative:** 豆瓣 has an official data export request (takes 24h):
`https://www.douban.com/mine/` → 账号与安全 → 个人数据申请

---

## B 站 (Bilibili)

**Strategy:** Intercept XHR API calls via Playwright (more reliable than DOM scraping)

**Key API endpoints (require login cookie):**
```
收藏夹列表: GET https://api.bilibili.com/x/v3/fav/folder/created/list-all
            ?up_mid={uid}&jsonp=jsonp
收藏夹内容: GET https://api.bilibili.com/x/v3/fav/resource/list
            ?media_id={fid}&ps=20&pn={page}&keyword=&order=mtime&type=0&tid=0
历史记录:   GET https://api.bilibili.com/x/web-interface/history/cursor
投币/点赞:  GET https://api.bilibili.com/x/space/coin/video?vmid={uid}&jsonp=jsonp
```

**Intercept pattern:**
```python
responses = []
page.on("response", lambda r: responses.append(r) if "api.bilibili.com" in r.url else None)
await page.goto("https://space.bilibili.com/")
# trigger API calls by navigating to 收藏 tab
await page.click('text=收藏')
await page.wait_for_timeout(2000)
for r in responses:
    if "fav/folder" in r.url:
        data = await r.json()
```

**Auth:** Requires `SESSDATA` and `bili_jct` cookies. Extract from browser after login.

**Rate limit:** Max 60 req/min. Use `asyncio.sleep(1)` between paginated calls.

---

## 小红书 (Xiaohongshu / RED)

**Strategy:** Playwright (web version) — harder due to anti-bot

**Key URLs:**
```
收藏:  https://www.xiaohongshu.com/user/profile/{uid}/collect
发布:  https://www.xiaohongshu.com/user/profile/{uid}
```

**Anti-detection notes:**
- Must use persistent context with real user profile to pass fingerprint check
- Randomise mouse movements before clicking: `page.mouse.move(x+rand, y+rand)`
- Set realistic viewport: `viewport={"width": 1440, "height": 900}`
- Add `navigator.webdriver = false` override via `page.add_init_script`

```python
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
""")
```

**Selectors:**
```python
note_cards  = ".note-item"          # may change; inspect after load
title       = ".title span"
cover_img   = "img.cover"           # use src URL to identify content
```

**Fallback:** Browser extension that captures DOM on page visit is more reliable.
Inject content script that listens for `document.querySelectorAll('.note-item')`
and POSTs to localhost server.

---

## 微信读书 (WeRead)

**Primary strategy: Local SQLite cache (most reliable)**

**macOS cache location:**
```
~/Library/Containers/com.tencent.WeReadMac/Data/Library/Application Support/WeRead/
```
Files: `*.db` (multiple databases; enumerate all)

**Key tables (varies by app version — always `PRAGMA table_info` first):**
```sql
-- Books
SELECT * FROM ZBOOK;              -- or book_info, WRBookInfo
-- Reading progress
SELECT * FROM ZREADINFO;          -- or reading_info
-- Highlights/notes
SELECT * FROM ZANNOTATION;        -- or bookmark, WRAnnotation
```

**Common column mappings:**
```python
book_id   → ZBOOKID or bookId
title     → ZTITLE or title  
author    → ZAUTHOR or author
progress  → ZREADINGPROGRESS or readingProgress  # 0-100
```

**Web version fallback (Playwright):**
```
https://weread.qq.com/
收藏: 书架 → 已读
```

**Windows path:**
```
C:\Users\{user}\AppData\Local\Tencent\WeRead\
```

---

## Kindle / Amazon

**Strategy A: My Clippings.txt (highlights & notes)**
```
Path: /Volumes/Kindle/documents/My Clippings.txt  # when Kindle plugged in
      ~/Documents/My Clippings.txt                 # some sync setups
```

Format:
```
Book Title (Author Name)
- Your Highlight on page 42 | Location 512-515 | Added on Monday, January 1, 2024

Highlighted text here.
==========
```

**Strategy B: Goodreads export (reading history)**
```
URL: https://www.goodreads.com/review/import
Format: CSV with columns: Title, Author, My Rating, Date Read, Bookshelves
```

**Strategy C: Amazon order/reading history**
```
URL: https://www.amazon.co.jp/hz/privacy-central/data-requests/preview
     Request "Your Orders" data export
```

---

## 抖音 (Douyin / TikTok)

**Strategy: Share-sheet link intake + metadata resolver**

Direct scraping is very hard (heavy JS fingerprinting, short-lived tokens).
Better UX: receive share links from user, resolve metadata server-side.

**Share URL format:**
```
https://v.douyin.com/XXXXXX/   # short link → redirects to full URL
```

**Resolve metadata:**
```python
import requests

def resolve_douyin(short_url):
    r = requests.get(short_url, allow_redirects=True,
                     headers={"User-Agent": "Mozilla/5.0"})
    # Extract from og: meta tags
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("meta", property="og:title")
    desc  = soup.find("meta", property="og:description")
    return {
        "title": title["content"] if title else "",
        "summary": desc["content"] if desc else "",
        "url": r.url,
    }
```

**iOS/Android intake:** Set up a local HTTP server on the Mac; configure Shortcuts app
to POST share-sheet URLs to `http://localhost:8765/intake`.

---

## 微博 (Weibo)

**Strategy:** Playwright — public profile pages are accessible without login for public accounts

**Key URLs:**
```
收藏: https://weibo.com/fav  (requires login)
```

**Selectors:**
```python
posts      = ".card-wrap"
text       = ".txt"
timestamp  = ".from a:first-child"
```

---

## Common anti-detection techniques

Read `references/anti-detection.md` for full details. Quick reference:

```python
# Randomise timing
import random, asyncio
await asyncio.sleep(random.uniform(0.8, 2.5))

# Human-like scroll
await page.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.3)")
await asyncio.sleep(random.uniform(0.5, 1.2))

# Realistic viewport
context = await pw.chromium.launch_persistent_context(
    viewport={"width": 1440, "height": 900},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    locale="zh-CN",
    timezone_id="Asia/Shanghai",
)
```
