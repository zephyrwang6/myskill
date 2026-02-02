#!/usr/bin/env python3
"""
抓取 X/Twitter 博主的推文内容

使用方法：
    python3 fetch_tweets.py <username> [--count 100] [--output tweets.json]

依赖：
    pip install playwright
    playwright install chromium
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='抓取 X/Twitter 博主推文')
    parser.add_argument('username', help='博主用户名（不含 @）')
    parser.add_argument('--count', type=int, default=100, help='抓取推文数量（默认 100）')
    parser.add_argument('--output', help='输出文件路径（默认 <username>_tweets.json）')
    parser.add_argument('--timeout', type=int, default=60, help='页面加载超时时间（秒）')
    return parser.parse_args()

def fetch_tweets(username: str, count: int = 100, timeout: int = 60) -> list:
    """
    使用 Playwright 抓取推文

    Returns:
        推文列表，每条推文包含：
        - text: 推文内容
        - time: 发布时间
        - likes: 点赞数
        - retweets: 转发数
        - replies: 回复数
        - has_media: 是否包含图片/视频
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误：请先安装 playwright")
        print("运行：pip install playwright && playwright install chromium")
        sys.exit(1)

    tweets = []
    url = f"https://x.com/{username}"

    print(f"正在访问 {url} ...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=timeout * 1000)
            page.wait_for_load_state('networkidle', timeout=timeout * 1000)

            # 等待推文加载
            page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)

            last_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 50

            while len(tweets) < count and scroll_attempts < max_scroll_attempts:
                # 获取当前页面的所有推文
                tweet_elements = page.query_selector_all('article[data-testid="tweet"]')

                for tweet_el in tweet_elements:
                    if len(tweets) >= count:
                        break

                    try:
                        # 提取推文文本
                        text_el = tweet_el.query_selector('[data-testid="tweetText"]')
                        text = text_el.inner_text() if text_el else ""

                        # 跳过已抓取的推文（通过内容去重）
                        if any(t['text'] == text for t in tweets):
                            continue

                        # 提取时间
                        time_el = tweet_el.query_selector('time')
                        tweet_time = time_el.get_attribute('datetime') if time_el else ""

                        # 提取互动数据
                        likes = 0
                        retweets = 0
                        replies = 0

                        # 点赞数
                        like_el = tweet_el.query_selector('[data-testid="like"] span')
                        if like_el:
                            likes = parse_count(like_el.inner_text())

                        # 转发数
                        retweet_el = tweet_el.query_selector('[data-testid="retweet"] span')
                        if retweet_el:
                            retweets = parse_count(retweet_el.inner_text())

                        # 回复数
                        reply_el = tweet_el.query_selector('[data-testid="reply"] span')
                        if reply_el:
                            replies = parse_count(reply_el.inner_text())

                        # 检查是否有媒体
                        has_media = tweet_el.query_selector('[data-testid="tweetPhoto"]') is not None or \
                                   tweet_el.query_selector('[data-testid="videoPlayer"]') is not None

                        tweets.append({
                            'text': text,
                            'time': tweet_time,
                            'likes': likes,
                            'retweets': retweets,
                            'replies': replies,
                            'has_media': has_media
                        })

                    except Exception as e:
                        print(f"解析推文时出错：{e}")
                        continue

                # 检查是否有新推文
                if len(tweets) == last_count:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    last_count = len(tweets)

                print(f"已抓取 {len(tweets)}/{count} 条推文...")

                # 向下滚动加载更多
                page.evaluate('window.scrollBy(0, 1000)')
                time.sleep(1)

        except Exception as e:
            print(f"抓取过程出错：{e}")
        finally:
            browser.close()

    return tweets

def parse_count(text: str) -> int:
    """解析互动数量（处理 K、M 后缀）"""
    if not text or text.strip() == '':
        return 0

    text = text.strip().upper()
    try:
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        else:
            return int(text.replace(',', ''))
    except:
        return 0

def main():
    args = parse_args()

    print(f"开始抓取 @{args.username} 的推文...")
    print(f"目标数量：{args.count} 条")

    tweets = fetch_tweets(args.username, args.count, args.timeout)

    if not tweets:
        print("未能抓取到任何推文，请检查：")
        print("1. 用户名是否正确")
        print("2. 账号是否公开")
        print("3. 网络是否可以访问 x.com")
        sys.exit(1)

    # 保存结果
    output_file = args.output or f"{args.username}_tweets.json"
    output_path = Path(output_file)

    result = {
        'username': args.username,
        'fetched_at': datetime.now().isoformat(),
        'total_count': len(tweets),
        'tweets': tweets
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n抓取完成！")
    print(f"共抓取 {len(tweets)} 条推文")
    print(f"保存到：{output_path}")

    # 输出简要统计
    total_likes = sum(t['likes'] for t in tweets)
    total_retweets = sum(t['retweets'] for t in tweets)
    media_count = sum(1 for t in tweets if t['has_media'])

    print(f"\n--- 简要统计 ---")
    print(f"总点赞：{total_likes:,}")
    print(f"总转发：{total_retweets:,}")
    print(f"含媒体推文：{media_count} 条 ({media_count/len(tweets)*100:.1f}%)")

if __name__ == '__main__':
    main()
