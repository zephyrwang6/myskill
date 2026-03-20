# Anti-Detection Techniques

Techniques to make Playwright automation less detectable. Use these for platforms that
actively fingerprint bots (小红书, 抖音, 微博).

## The key principle

We are operating in the user's authenticated session — this is legally and ethically distinct
from server-side scraping. The goal is not to deceive the platform, but to avoid triggering
automated bot-detection that would block legitimate user data access.

---

## Browser fingerprint hardening

```python
async def create_stealthy_context(pw):
    context = await pw.chromium.launch_persistent_context(
        user_data_dir="/tmp/harvest-profile",   # persistent = real cookies
        headless=False,                          # headless is more detectable
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        color_scheme="light",
        device_scale_factor=2.0,                # retina display
    )

    # Patch webdriver flag on every new page
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.chrome = {runtime: {}};
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]   // non-zero plugin count
        });
    """)
    return context
```

---

## Timing jitter

Never use fixed delays — they're a bot signature.

```python
import random, asyncio

async def human_delay(min_ms=800, max_ms=2500):
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000)

async def human_scroll(page, distance_ratio=0.4):
    """Scroll partway down, pause, scroll more — like a human reading."""
    height = await page.evaluate("document.body.scrollHeight")
    target = int(height * distance_ratio)
    step   = random.randint(200, 500)
    pos    = 0
    while pos < target:
        pos = min(pos + step, target)
        await page.evaluate(f"window.scrollTo(0, {pos})")
        await asyncio.sleep(random.uniform(0.05, 0.15))
    await human_delay(500, 1500)
```

---

## Mouse movement before clicks

```python
async def human_click(page, selector):
    el = await page.wait_for_selector(selector)
    box = await el.bounding_box()
    # Move to element with slight overshoot
    cx = box["x"] + box["width"]/2 + random.uniform(-5, 5)
    cy = box["y"] + box["height"]/2 + random.uniform(-3, 3)
    await page.mouse.move(cx - 50, cy - 20)
    await human_delay(100, 300)
    await page.mouse.move(cx, cy)
    await human_delay(80, 200)
    await page.mouse.click(cx, cy)
```

---

## Session management

```python
# Save cookies after login to avoid re-login
import json, pathlib

COOKIE_FILE = pathlib.Path.home() / ".personal-harvest" / "cookies.json"

async def save_cookies(context, platform):
    cookies = await context.cookies()
    data = json.loads(COOKIE_FILE.read_text()) if COOKIE_FILE.exists() else {}
    data[platform] = cookies
    COOKIE_FILE.write_text(json.dumps(data, indent=2))

async def load_cookies(context, platform):
    if not COOKIE_FILE.exists(): return
    data = json.loads(COOKIE_FILE.read_text())
    if platform in data:
        await context.add_cookies(data[platform])
```

---

## Rate limiting per platform

| Platform | Safe request rate | Cooldown if blocked |
|---|---|---|
| 豆瓣 | 1 req / 1-2s | 10 min pause |
| B 站 API | 60 req / min | 5 min pause |
| 小红书 | 1 req / 3-5s | 30 min pause |
| 微博 | 1 req / 2s | 10 min pause |

```python
# Exponential backoff on HTTP 429 or captcha detection
async def with_backoff(coro, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await coro
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) * random.uniform(30, 60)
            print(f"Backing off {wait:.0f}s after error: {e}")
            await asyncio.sleep(wait)
```

---

## Captcha handling

When a captcha appears, the agent should:
1. Take a screenshot and surface it to the user
2. Launch non-headless browser so user can solve manually
3. Resume after user signals completion

```python
async def check_for_captcha(page):
    captcha_selectors = [
        "iframe[src*='captcha']",
        ".geetest_panel",
        "#captcha-box",
        "text=请完成安全验证",
    ]
    for sel in captcha_selectors:
        if await page.query_selector(sel):
            await page.screenshot(path="captcha_detected.png")
            print("⚠️  Captcha detected. Please solve it in the browser window.")
            input("Press Enter when solved...")
            return True
    return False
```
