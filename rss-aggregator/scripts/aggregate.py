import argparse
import datetime
import feedparser
import xml.etree.ElementTree as ET
import concurrent.futures
import time
import sys
import os
import re
from html import unescape

def clean_summary(summary, max_chars=1500):
    if not summary:
        return "No summary available."
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', summary)
    # Unescape HTML entities
    text = unescape(text)
    # Collapse whitespace
    text = ' '.join(text.split())
    # Truncate to max_chars
    if len(text) > max_chars:
        return text[:max_chars-3] + "..."
    return text

def parse_opml(opml_path):
    urls = []
    try:
        tree = ET.parse(opml_path)
        root = tree.getroot()
        for outline in root.findall(".//outline"):
            url = outline.get('xmlUrl')
            if url:
                # Clean up any potential whitespace or quotes if parser didn't
                url = url.strip().strip('`').strip('"').strip("'")
                urls.append(url)
    except Exception as e:
        print(f"Error parsing OPML: {e}", file=sys.stderr)
    return urls

def get_entry_date(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
    return None

def process_feed(url, cutoff_date):
    updates = []
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries: # bozo means error but sometimes entries are parsed anyway
             return []
        
        feed_title = feed.feed.get('title', url)
        
        for entry in feed.entries:
            entry_date = get_entry_date(entry)
            if not entry_date:
                continue
            
            if entry_date >= cutoff_date:
                summary = entry.get('summary', entry.get('description', ''))
                updates.append({
                    'feed_title': feed_title,
                    'title': entry.get('title', 'No Title'),
                    'author': entry.get('author', feed.feed.get('author', 'Unknown')),
                    'summary': clean_summary(summary),
                    'updated': entry_date,
                    'link': entry.get('link', '')
                })
    except Exception as e:
        # Silently fail for individual feeds to keep output clean, or log to stderr
        # print(f"Error processing {url}: {e}", file=sys.stderr)
        pass
    return updates

def main():
    parser = argparse.ArgumentParser(description='RSS Aggregator')
    parser.add_argument('--days', type=int, default=3, help='Number of days to look back')
    parser.add_argument('--opml', type=str, default='references/feeds.opml', help='Path to OPML file')
    args = parser.parse_args()

    # Resolve OPML path relative to script location if needed
    # Assuming script is run from skill root or handled by caller.
    # If run as `uv run scripts/aggregate.py`, relative path `references/feeds.opml` works if cwd is skill root.
    # If cwd is arbitrary, we should find opml relative to script.
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    opml_path = args.opml
    if not os.path.isabs(opml_path):
        # Try relative to CWD first, then relative to script parent (skill root)
        if not os.path.exists(opml_path):
             skill_root = os.path.dirname(script_dir)
             opml_path = os.path.join(skill_root, args.opml)

    if not os.path.exists(opml_path):
        print(f"OPML file not found: {opml_path}", file=sys.stderr)
        sys.exit(1)

    urls = parse_opml(opml_path)
    if not urls:
        print("No URLs found in OPML.", file=sys.stderr)
        sys.exit(0)

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
    
    print(f"Checking {len(urls)} feeds for updates since {cutoff_date.strftime('%Y-%m-%d')}...")

    all_updates = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(process_feed, url, cutoff_date): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            all_updates.extend(data)

    # Sort by date descending
    all_updates.sort(key=lambda x: x['updated'], reverse=True)

    if not all_updates:
        print("No updates found.")
        return

    print(f"\nFound {len(all_updates)} updates:\n")
    for item in all_updates:
        print(f"### {item['title']}")
        print(f"- **Source**: {item['feed_title']}")
        print(f"- **Author**: {item['author']}")
        print(f"- **Date**: {item['updated'].strftime('%Y-%m-%d %H:%M')}")
        print(f"- **Link**: {item['link']}")
        print(f"- **Summary**: {item['summary']}")
        print()

if __name__ == '__main__':
    main()
