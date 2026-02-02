#!/usr/bin/env python3
"""
获取关注的 YouTube 博主最近更新
用法: python get_updates.py [--days 2]
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import argparse
import json

# 关注的 YouTube 频道列表 (来自 Zara's AI Learning Library)
# 格式: (名称, channel_id, 频道URL)
CHANNELS = [
    # === AI 教育 & 技术深度 ===
    ("Andrej Karpathy", "UCXUPKJO5MZQN11PqgIvyuvQ", "@AndrejKarpathy"),
    ("Anthropic", "UCrDwWp7EBBv4NwvScIpBDOA", "@anthropic-ai"),
    ("Lex Fridman", "UCGwuxdEeCf0TIA2RbPOj-8g", "@lexfridman"),
    
    # === AI 产品 & 创业 ===
    ("Lenny's Podcast", "UCcIXPgBDgKd5EbfWi4i5cVA", "@LennysPodcast"),
    ("Peter Yang", "UCSHZKyawb77ixDdsGog4iWA", "@PeterYangYT"),
    ("The MAD Podcast (Matt Turck)", "UCQID78IY6EOojr5RUdD47MQ", "@DataDrivenNYC"),
    ("Every", "UCXZFVVCFahewxr3est7aT7Q", "@EveryInc"),
    
    # === VC & 投资人 ===
    ("Y Combinator", "UCcefcZRL2oaA_uBNeo5UOWg", "@ycombinator"),
    ("Latent Space", "UCwBTFE_6Bsb_EtmXlW2aTlg", "@LatentSpacePod"),
    ("South Park Commons", "UCnpBg7yqNauHtlNSpOl5-cg", "@southparkcommons"),
    ("No Priors", "UC4Snw5yrSDMXys31I18U3gg", "@NoPriorsPodcast"),
    ("a16z", "UCE_b6sxLv68tda7tvv5YWuA", "@a16z"),
    
    # === 大厂 & 研究 ===
    ("Google DeepMind", "UCP7jMXSY2xbc3KCAE0MHQ-A", "@googledeepmind"),
    ("Google for Developers", "UC_x5XG1OV2P6uZZ5FSM9Ttw", "@GoogleDevelopers"),
    ("Stanford GSB", "UCjIMtrzxYc0lblGhmOgC_CA", "@stanfordgsb"),
    
    # === Vibe Coding & 工具 ===
    ("Mckay Wrigley", "UCbGt-LT2R9hglFeTr6KuXkw", "@realmckaywrigley"),
    ("Tiago Forte", "UCxBcwypKK-W3GHd_RZ9FZrQ", "@TiagoForte"),
    ("The Pragmatic Engineer", "UCWG5I2nL7zyrRj6bCy5qC7A", "@ThePragmaticEngineer"),
    
    # === AI 新闻 & 趋势 ===
    ("The AI Daily Brief", "UCIAtPXNxXPKmw-_1sYnrJzQ", "@TheAIDailyBrief"),
    ("TBPN", "UCQvWX73GQygcwXOTSf_VDVg", "@TBPNLive"),
    ("Brett Malinowski", "UCMR-rPSUI34DRQXUkvFuIUQ", "@TheBrettWay"),
]


def get_channel_feed(channel_id):
    """获取频道的 RSS feed"""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"获取 feed 失败: {e}")
    return None


def parse_feed(xml_content, channel_name, days=2):
    """解析 RSS feed，获取最近 N 天的视频"""
    videos = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    try:
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 
              'media': 'http://search.yahoo.com/mrss/',
              'yt': 'http://www.youtube.com/xml/schemas/2015'}
        
        for entry in root.findall('atom:entry', ns):
            published = entry.find('atom:published', ns)
            if published is not None:
                pub_date = datetime.fromisoformat(published.text.replace('Z', '+00:00'))
                pub_date_naive = pub_date.replace(tzinfo=None)
                
                if pub_date_naive >= cutoff_date:
                    title = entry.find('atom:title', ns)
                    video_id = entry.find('yt:videoId', ns)
                    
                    # 获取视频描述信息
                    media_group = entry.find('media:group', ns)
                    description = ""
                    if media_group is not None:
                        desc_elem = media_group.find('media:description', ns)
                        if desc_elem is not None and desc_elem.text:
                            description = desc_elem.text[:1500]  # 获取更多描述以生成更详细的摘要
                    
                    videos.append({
                        'channel': channel_name,
                        'title': title.text if title is not None else 'Unknown',
                        'video_id': video_id.text if video_id is not None else '',
                        'published': pub_date_naive.strftime('%Y-%m-%d %H:%M'),
                        'url': f"https://www.youtube.com/watch?v={video_id.text}" if video_id is not None else '',
                        'description': description
                    })
    except Exception as e:
        print(f"解析失败: {e}")
    
    return videos


def get_video_details(video_id):
    """获取视频详情：播放数和时长"""
    result = {'views': None, 'duration': None}
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            import re
            # 获取观看次数
            match = re.search(r'"viewCount":"(\d+)"', response.text)
            if match:
                views = int(match.group(1))
                if views >= 1000000:
                    result['views'] = f"{views/1000000:.1f}M"
                elif views >= 1000:
                    result['views'] = f"{views/1000:.1f}K"
                else:
                    result['views'] = str(views)
            
            # 获取视频时长（秒）
            duration_match = re.search(r'"lengthSeconds":"(\d+)"', response.text)
            if duration_match:
                seconds = int(duration_match.group(1))
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                if hours > 0:
                    result['duration'] = f"{hours}h{minutes:02d}m"
                else:
                    result['duration'] = f"{minutes}分钟"
    except:
        pass
    return result


def generate_summary(description, title, max_chars=400):
    """从描述中提取摘要，默认 400 字"""
    if not description:
        return f"关于「{title}」的最新视频内容，点击链接观看完整视频。"
    
    # 清理描述文本
    lines = description.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        # 跳过链接行、订阅提示、空行、时间戳
        if not line:
            continue
        if line.startswith('http') or line.startswith('Subscribe') or line.startswith('→'):
            continue
        if 'subscribe' in line.lower() or 'goo.gle' in line.lower():
            continue
        if line.startswith('0:') or line.startswith('1:') or line.startswith('2:'):  # 跳过时间戳
            continue
        if line.startswith('#') and len(line) < 30:  # 跳过短标签
            continue
        clean_lines.append(line)
    
    # 合并成摘要
    summary = ' '.join(clean_lines)
    
    # 截取到合适长度，保持句子完整
    if len(summary) > max_chars:
        # 尝试在句号、问号、感叹号处截断
        for end_char in ['。', '！', '？', '. ', '! ', '? ', '— ', ': ']:
            pos = summary[:max_chars].rfind(end_char)
            if pos > max_chars * 0.6:  # 至少保留 60% 内容
                return summary[:pos+1]
        # 否则直接截断
        return summary[:max_chars] + '...'
    
    return summary if summary else f"关于「{title}」的最新视频内容，点击链接观看完整视频。"


def main():
    parser = argparse.ArgumentParser(description='获取关注的 YouTube 博主最近更新')
    parser.add_argument('--days', type=int, default=2, help='获取最近 N 天的更新 (默认: 2)')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    parser.add_argument('--markdown', action='store_true', help='以 Markdown 格式输出')
    parser.add_argument('--views', action='store_true', help='获取播放量（会增加请求时间）')
    args = parser.parse_args()
    
    all_videos = []
    
    import sys
    print(f"正在获取最近 {args.days} 天的播客更新...", file=sys.stderr)
    
    for name, channel_id, handle in CHANNELS:
        feed = get_channel_feed(channel_id)
        if feed:
            videos = parse_feed(feed, name, args.days)
            all_videos.extend(videos)
    
    # 按发布时间排序
    all_videos.sort(key=lambda x: x['published'], reverse=True)
    
    # 添加摘要
    for video in all_videos:
        video['summary'] = generate_summary(video['description'], video['title'])
    
    # 获取播放量和时长（可选）
    if args.views:
        print(f"正在获取播放量和时长...", file=sys.stderr)
        import time
        for video in all_videos:
            details = get_video_details(video['video_id'])
            video['views'] = details['views'] if details['views'] else '-'
            video['duration'] = details['duration'] if details['duration'] else '-'
            time.sleep(0.3)
    
    if args.json:
        print(json.dumps(all_videos, ensure_ascii=False, indent=2))
    elif args.markdown:
        # Markdown 格式输出
        if not all_videos:
            print(f"最近 {args.days} 天没有新的播客更新。")
            return
        
        print(f"## 📺 最近 {args.days} 天共有 {len(all_videos)} 个新播客更新\n")
        
        for i, video in enumerate(all_videos, 1):
            date_short = video['published'].split(' ')[0][5:]  # MM-DD
            duration_str = f" | ⏱ {video.get('duration')}" if video.get('duration') else ""
            views_str = f" | 👁 {video.get('views')}" if video.get('views') else ""
            print(f"### {i}. [{video['title']}]({video['url']})")
            print(f"**{video['channel']}** | {date_short}{duration_str}{views_str}\n")
            print(f"> {video['summary']}\n")
            print("---\n")
    else:
        # 默认格式输出
        if not all_videos:
            print(f"最近 {args.days} 天没有新的播客更新。")
            return
        
        print(f"\n📺 最近 {args.days} 天共有 {len(all_videos)} 个新播客更新：\n")
        print("=" * 70)
        
        for i, video in enumerate(all_videos, 1):
            date_short = video['published'].split(' ')[0][5:]  # MM-DD
            duration_str = f" | ⏱ {video.get('duration')}" if video.get('duration') else ""
            views_str = f" | 👁 {video.get('views')}" if video.get('views') else ""
            print(f"\n{i}. 【{video['channel']}】{date_short}{duration_str}{views_str}")
            print(f"   📌 {video['title']}")
            print(f"   🔗 {video['url']}")
            print(f"   📝 {video['summary']}")
            print("-" * 70)


if __name__ == "__main__":
    main()
