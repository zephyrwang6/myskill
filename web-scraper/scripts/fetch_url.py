#!/usr/bin/env python3
"""
Web page fetcher that extracts main content from URLs.
Uses requests library for better compatibility with various websites.
Converts HTML to clean markdown text.
"""

import sys
import argparse
import re
from html.parser import HTMLParser
from typing import Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error
    import ssl


class HTMLToMarkdown(HTMLParser):
    """Convert HTML to simplified markdown."""

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_tag = None
        self.in_script = False
        self.in_style = False
        self.in_nav = False
        self.in_footer = False
        self.in_aside = False
        self.list_depth = 0
        self.ordered_list_counter = 0
        self.ignore_tags = {'script', 'style', 'nav', 'footer', 'aside', 'noscript', 'iframe', 'svg', 'path', 'button', 'form', 'input'}
        self.block_tags = {'p', 'div', 'article', 'section', 'main', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'pre', 'br', 'tr'}

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

        if tag in self.ignore_tags:
            if tag == 'script':
                self.in_script = True
            elif tag == 'style':
                self.in_style = True
            elif tag == 'nav':
                self.in_nav = True
            elif tag == 'footer':
                self.in_footer = True
            elif tag == 'aside':
                self.in_aside = True
            return

        if self.in_script or self.in_style or self.in_nav or self.in_footer or self.in_aside:
            return

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.result.append('\n\n' + '#' * level + ' ')
        elif tag == 'p':
            self.result.append('\n\n')
        elif tag == 'br':
            self.result.append('\n')
        elif tag == 'li':
            if self.ordered_list_counter:
                self.result.append(f'\n{self.ordered_list_counter}. ')
                self.ordered_list_counter += 1
            else:
                self.result.append('\n- ')
        elif tag == 'ul':
            self.list_depth += 1
            self.ordered_list_counter = 0
        elif tag == 'ol':
            self.list_depth += 1
            self.ordered_list_counter = 1
        elif tag == 'blockquote':
            self.result.append('\n\n> ')
        elif tag == 'pre':
            self.result.append('\n\n```\n')
        elif tag == 'code':
            if self.current_tag != 'pre':
                self.result.append('`')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                self.result.append('[')
        elif tag == 'img':
            attrs_dict = dict(attrs)
            alt = attrs_dict.get('alt', '')
            if alt:
                self.result.append(f'[Image: {alt}]')
        elif tag == 'td' or tag == 'th':
            self.result.append(' | ')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag == 'nav':
            self.in_nav = False
        elif tag == 'footer':
            self.in_footer = False
        elif tag == 'aside':
            self.in_aside = False

        if self.in_script or self.in_style or self.in_nav or self.in_footer or self.in_aside:
            return

        if tag in ('ul', 'ol'):
            self.list_depth -= 1
            if tag == 'ol':
                self.ordered_list_counter = 0
            self.result.append('\n')
        elif tag == 'pre':
            self.result.append('\n```\n\n')
        elif tag == 'code':
            self.result.append('`')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'a':
            self.result.append(']')
        elif tag in self.block_tags:
            self.result.append('\n')

        self.current_tag = None

    def handle_data(self, data):
        if self.in_script or self.in_style or self.in_nav or self.in_footer or self.in_aside:
            return
        text = data.strip()
        if text:
            self.result.append(text + ' ')

    def get_markdown(self) -> str:
        text = ''.join(self.result)
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n +', '\n', text)
        text = re.sub(r'\[\s*\]', '', text)  # Remove empty links
        return text.strip()


def fetch_with_requests(url: str, timeout: int = 30) -> str:
    """Fetch using requests library."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Accept-Encoding': 'identity',  # Request uncompressed content
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Try to detect encoding
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"


def fetch_with_urllib(url: str, timeout: int = 30) -> str:
    """Fallback fetch using urllib."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ctx) as response:
            content_type = response.headers.get('Content-Type', '')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1].split(';')[0].strip()
            return response.read().decode(encoding, errors='replace')

    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return f"URL Error: {e.reason}"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch content from a URL and return as markdown."""
    if HAS_REQUESTS:
        html_content = fetch_with_requests(url, timeout)
    else:
        html_content = fetch_with_urllib(url, timeout)

    # Check if it's an error message
    if html_content.startswith("Error") or html_content.startswith("HTTP Error") or html_content.startswith("URL Error"):
        return html_content

    # Convert to markdown
    parser = HTMLToMarkdown()
    parser.feed(html_content)
    return parser.get_markdown()


def main():
    parser = argparse.ArgumentParser(description='Fetch web page content and convert to markdown')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    parser.add_argument('--max-length', type=int, default=100000, help='Maximum output length (default: 100000)')
    parser.add_argument('--raw', action='store_true', help='Output raw HTML instead of markdown')

    args = parser.parse_args()

    if args.raw:
        if HAS_REQUESTS:
            content = fetch_with_requests(args.url, timeout=args.timeout)
        else:
            content = fetch_with_urllib(args.url, timeout=args.timeout)
    else:
        content = fetch_url(args.url, timeout=args.timeout)

    # Truncate if too long
    if len(content) > args.max_length:
        content = content[:args.max_length] + "\n\n[Content truncated...]"

    print(content)


if __name__ == '__main__':
    main()
