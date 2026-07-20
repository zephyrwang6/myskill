---
name: baoyu-danger-x-to-markdown
description: Converts X (Twitter) tweets and articles to markdown with YAML front matter. Uses reverse-engineered API requiring user consent. Use when user mentions "X to markdown", "tweet to markdown", "save tweet", or provides x.com/twitter.com URLs for conversion.
---

# X to Markdown

Converts X content to markdown:
- Tweets/threads → Markdown with YAML front matter
- X Articles → Full content extraction

## Script Directory

Scripts located in `scripts/` subdirectory.

**Path Resolution**:
1. `SKILL_DIR` = this SKILL.md's directory
2. Script path = `${SKILL_DIR}/scripts/main.ts`

## Consent Requirement

**Before any conversion**, check and obtain consent.

### Consent Flow

**Step 1**: Check consent file

```bash
# macOS
cat ~/Library/Application\ Support/baoyu-skills/x-to-markdown/consent.json

# Linux
cat ~/.local/share/baoyu-skills/x-to-markdown/consent.json
```

**Step 2**: If `accepted: true` and `disclaimerVersion: "1.0"` → print warning and proceed:
```
Warning: Using reverse-engineered X API. Accepted on: <acceptedAt>
```

**Step 3**: If missing or version mismatch → display disclaimer:
```
DISCLAIMER

This tool uses a reverse-engineered X API, NOT official.

Risks:
- May break if X changes API
- No guarantees or support
- Possible account restrictions
- Use at your own risk

Accept terms and continue?
```

Use `AskUserQuestion` with options: "Yes, I accept" | "No, I decline"

**Step 4**: On accept → create consent file:
```json
{
  "version": 1,
  "accepted": true,
  "acceptedAt": "<ISO timestamp>",
  "disclaimerVersion": "1.0"
}
```

**Step 5**: On decline → output "User declined. Exiting." and stop.

## Reviewed Source Packet Mode

If the user provides a reviewed public source packet instead of an X/Twitter
URL, do not run the script, open Chrome, or request authentication. Convert the
packet fields directly into Markdown.

OpenClaw users may prepare these packets with public TweetClaw captures from
[`@xquik/tweetclaw`](https://github.com/Xquik-dev/tweetclaw). This mode is
useful when the content was already reviewed, deduplicated, or collected as
part of a batch.

Required packet fields:

| Field | Purpose |
|-------|---------|
| `source_url` | Original public X/Twitter post URL |
| `author` | Public handle or display name |
| `captured_at` | Collection or review time |
| `text` | Post or thread text |

Optional packet fields:

| Field | Purpose |
|-------|---------|
| `source` | Capture provider; default to `reviewed_packet` when omitted |
| `public_metrics` | Reviewed public counts when relevant |
| `notes` | Why this source belongs in the markdown set |

Markdown front matter for packet mode:

```yaml
---
source: "tweetclaw"
source_url: "https://x.com/user/status/123"
author: "Name (@user)"
captured_at: "2026-07-09T00:00:00Z"
public_metrics:
  likes: 42
---
```

Rules:

- Keep source-packet Markdown separate from fresh script output
- Preserve packet field names and values in front matter
- Omit optional fields when the packet does not provide them
- Do not infer private engagement, private sentiment, or non-public account data
- Do not ask for cookies, API keys, or browser login when a packet has enough text

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

## Preferences (EXTEND.md)

Use Bash to check EXTEND.md existence (priority order):

```bash
# Check project-level first
test -f .baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md && echo "project"

# Then user-level (cross-platform: $HOME works on macOS/Linux/WSL)
test -f "$HOME/.baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md" && echo "user"
```

┌────────────────────────────────────────────────────────────┬───────────────────┐
│                            Path                            │     Location      │
├────────────────────────────────────────────────────────────┼───────────────────┤
│ .baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md         │ Project directory │
├────────────────────────────────────────────────────────────┼───────────────────┤
│ $HOME/.baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md   │ User home         │
└────────────────────────────────────────────────────────────┴───────────────────┘

┌───────────┬───────────────────────────────────────────────────────────────────────────┐
│  Result   │                                  Action                                   │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ Found     │ Read, parse, apply settings                                               │
├───────────┼───────────────────────────────────────────────────────────────────────────┤
│ Not found │ **MUST** run first-time setup (see below) - do NOT silently create defaults │
└───────────┴───────────────────────────────────────────────────────────────────────────┘

**EXTEND.md Supports**: Download media by default | Default output directory

### First-Time Setup (BLOCKING)

**CRITICAL**: When EXTEND.md is not found, you **MUST use `AskUserQuestion`** to ask the user for their preferences before creating EXTEND.md. **NEVER** create EXTEND.md with defaults without asking. This is a **BLOCKING** operation - do NOT proceed with any conversion until setup is complete.

Use `AskUserQuestion` with ALL questions in ONE call:

**Question 1** - header: "Media", question: "How to handle images and videos in tweets?"
- "Ask each time (Recommended)" - After saving markdown, ask whether to download media
- "Always download" - Always download media to local imgs/ and videos/ directories
- "Never download" - Keep original remote URLs in markdown

**Question 2** - header: "Output", question: "Default output directory?"
- "x-to-markdown (Recommended)" - Save to ./x-to-markdown/{username}/{tweet-id}.md
- (User may choose "Other" to type a custom path)

**Question 3** - header: "Save", question: "Where to save preferences?"
- "User (Recommended)" - ~/.baoyu-skills/ (all projects)
- "Project" - .baoyu-skills/ (this project only)

After user answers, create EXTEND.md at the chosen location, confirm "Preferences saved to [path]", then continue.

Full reference: [references/config/first-time-setup.md](references/config/first-time-setup.md)

### Supported Keys

| Key | Default | Values | Description |
|-----|---------|--------|-------------|
| `download_media` | `ask` | `ask` / `1` / `0` | `ask` = prompt each time, `1` = always download, `0` = never |
| `default_output_dir` | empty | path or empty | Default output directory (empty = `./x-to-markdown/`) |

**Value priority**:
1. CLI arguments (`--download-media`, `-o`)
2. EXTEND.md
3. Skill defaults

## Usage

```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts <url>
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> -o output.md
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> --download-media
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> --json
```

## Options

| Option | Description |
|--------|-------------|
| `<url>` | Tweet or article URL |
| `-o <path>` | Output path |
| `--json` | JSON output |
| `--download-media` | Download image/video assets to local `imgs/` and `videos/`, and rewrite markdown links to local relative paths |
| `--login` | Refresh cookies only |

## Supported URLs

- `https://x.com/<user>/status/<id>`
- `https://twitter.com/<user>/status/<id>`
- `https://x.com/i/article/<id>`

## Output

```markdown
---
url: "https://x.com/user/status/123"
author: "Name (@user)"
tweetCount: 3
coverImage: "https://pbs.twimg.com/media/example.jpg"
---

Content...
```

**File structure**: `x-to-markdown/{username}/{tweet-id}.md`

When `--download-media` is enabled:
- Images are saved to `imgs/` next to the markdown file
- Videos are saved to `videos/` next to the markdown file
- Markdown media links are rewritten to local relative paths

## Media Download Workflow

Based on `download_media` setting in EXTEND.md:

| Setting | Behavior |
|---------|----------|
| `1` (always) | Run script with `--download-media` flag |
| `0` (never) | Run script without `--download-media` flag |
| `ask` (default) | Follow the ask-each-time flow below |

### Ask-Each-Time Flow

1. Run script **without** `--download-media` → markdown saved
2. Check saved markdown for remote media URLs (`https://` in image/video links)
3. **If no remote media found** → done, no prompt needed
4. **If remote media found** → use `AskUserQuestion`:
   - header: "Media", question: "Download N images/videos to local files?"
   - "Yes" - Download to local directories
   - "No" - Keep remote URLs
5. If user confirms → run script **again** with `--download-media` (overwrites markdown with localized links)

## Authentication

1. **Environment variables** (preferred): `X_AUTH_TOKEN`, `X_CT0`
2. **Chrome login** (fallback): Auto-opens Chrome, caches cookies locally

## Extension Support

Custom configurations via EXTEND.md. See **Preferences** section for paths and supported options.
