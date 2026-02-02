#!/usr/bin/env python3
"""
Markdown to Image Converter - 杂志风格知识卡片
将 Markdown 内容转换为精美的图片海报，适合社交媒体分享。
"""

import argparse
import os
import re
import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright


# 小红书比例 3:4
CARD_WIDTH = 1080
CARD_HEIGHT = 1440  # 最小高度

# 水印信息
WATERMARK_AUTHOR = "@产品星球"
WATERMARK_DATE = datetime.now().strftime("%Y-%m-%d")
FOOTER_NOTE = "完整对话内容在产品星球知识库"


def get_html_template(content: str, page_num: int = 0, total_pages: int = 1, 
                      cover_image_url: str = None, is_last_page: bool = False) -> str:
    """返回完整的 HTML 模板"""
    
    # 封面图片 HTML（完整显示，不裁剪）
    cover_html = ''
    if cover_image_url and page_num == 0:
        cover_html = f'''
        <div class="cover-image">
            <img src="{cover_image_url}" alt="cover" />
        </div>
        '''
    
    # 页码指示器
    page_indicator = ''
    if total_pages > 1:
        page_indicator = f'<span class="page-num">{page_num + 1}/{total_pages}</span>'
    
    # 最后一页的额外提示
    footer_note_html = ''
    if is_last_page:
        footer_note_html = f'<div class="footer-note">{FOOTER_NOTE}</div>'
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700;900&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #f5f3ef;
            width: {CARD_WIDTH}px;
            min-height: {CARD_HEIGHT}px;
            padding: 28px;
        }}
        
        .card {{
            background: white;
            border-radius: 20px;
            padding: 36px 32px 24px 32px;
            min-height: calc({CARD_HEIGHT}px - 56px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            display: flex;
            flex-direction: column;
        }}
        
        .cover-image {{
            width: 100%;
            border-radius: 14px;
            overflow: hidden;
            margin-bottom: 28px;
            background: #f0f0f0;
        }}
        
        .cover-image img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        h1 {{
            font-size: 52px;
            font-weight: 900;
            color: #1a1a1a;
            margin-bottom: 24px;
            line-height: 1.35;
            letter-spacing: 1px;
        }}
        
        h1::after {{
            content: '';
            display: block;
            width: 80px;
            height: 5px;
            background: linear-gradient(90deg, #d4a574, #e8c9a8);
            margin-top: 20px;
            border-radius: 3px;
        }}
        
        h2 {{
            font-size: 44px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 36px;
            line-height: 1.35;
            letter-spacing: 0.5px;
        }}
        
        h2::after {{
            content: '';
            display: block;
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, #d4a574, #e8c9a8);
            margin-top: 18px;
            border-radius: 2px;
        }}
        
        .intro {{
            font-size: 30px;
            line-height: 1.9;
            color: #444;
            margin-bottom: 28px;
            padding-bottom: 24px;
            border-bottom: 1px solid #eee;
            letter-spacing: 0.8px;
        }}
        
        .transition {{
            font-size: 26px;
            color: #888;
            margin-bottom: 28px;
            letter-spacing: 0.5px;
        }}
        
        .points-container {{
            flex: 1;
        }}
        
        .point {{
            margin-bottom: 36px;
        }}
        
        .point:last-child {{
            margin-bottom: 20px;
        }}
        
        .point-header {{
            display: flex;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 12px;
        }}
        
        .point-number {{
            font-size: 34px;
            font-weight: 800;
            color: #d4a574;
            min-width: 50px;
            letter-spacing: 0;
        }}
        
        .point-title {{
            font-size: 34px;
            font-weight: 700;
            color: #1a1a1a;
            line-height: 1.5;
            flex: 1;
            letter-spacing: 0.8px;
        }}
        
        .point-content {{
            font-size: 28px;
            color: #555;
            line-height: 1.85;
            margin-left: 66px;
            margin-top: 10px;
            letter-spacing: 0.8px;
        }}
        
        .footer {{
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        
        .footer-note {{
            font-size: 22px;
            color: #999;
            text-align: center;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}
        
        .footer-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 22px;
        }}
        
        .footer-left {{
            color: #aaa;
        }}
        
        .footer-right {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .page-num {{
            color: #bbb;
            font-size: 20px;
        }}
        
        .watermark {{
            color: #d4a574;
            font-weight: 600;
            font-size: 24px;
        }}
        
        strong, b {{
            font-weight: 700;
            color: #1a1a1a;
        }}
        
        code {{
            background: #f8f6f4;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 26px;
            color: #c7254e;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="card">
        {cover_html}
        {content}
        <div class="footer">
            {footer_note_html}
            <div class="footer-bottom">
                <span class="footer-left">{WATERMARK_DATE}</span>
                <div class="footer-right">
                    {page_indicator}
                    <span class="watermark">{WATERMARK_AUTHOR}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''


def parse_content_to_points(md_content: str) -> dict:
    """解析 Markdown 内容，提取标题、简介和核心观点"""
    lines = md_content.strip().split('\n')
    
    result = {
        'title': '',
        'short_title': '',  # 冒号后的短标题（用于续页）
        'intro': '',
        'points': [],
        'youtube_url': ''
    }
    
    point_buffer = []
    intro_lines = []
    found_first_point = False
    
    point_pattern = r'^(\d{1,2})[、\.\)）]\s*(.+)$'
    
    # 先扫描全文找 YouTube URL
    youtube_pattern = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+)'
    for line in lines:
        yt_match = re.search(youtube_pattern, line)
        if yt_match:
            result['youtube_url'] = yt_match.group(1)
            break
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('# 精华') or line.startswith('# 精彩'):
            break
        
        if line == '---':
            if found_first_point:
                break
            continue
        
        if not line:
            continue
        
        # 主标题 - 保留原始标题
        if line.startswith('# ') and not result['title']:
            title = line[2:].strip()
            result['title'] = title  # 使用原始标题
            
            # 提取冒号后的短标题（用于续页）
            # 先去掉日期前缀再取冒号后内容
            title_without_date = re.sub(r'^\d{4}[：:]\s*', '', title)
            if '：' in title_without_date:
                result['short_title'] = title_without_date.split('：', 1)[1].strip()
            elif ':' in title_without_date:
                result['short_title'] = title_without_date.split(':', 1)[1].strip()
            else:
                result['short_title'] = title_without_date[:20] + '...' if len(title_without_date) > 20 else title_without_date
            continue
        
        # 核心观点
        match = re.match(point_pattern, line)
        if match:
            found_first_point = True
            
            if point_buffer:
                result['points'].append({
                    'number': point_buffer[0],
                    'title': point_buffer[1],
                    'content': ' '.join(point_buffer[2:]) if len(point_buffer) > 2 else ''
                })
                point_buffer = []
            
            num = match.group(1)
            title_text = match.group(2).strip()
            
            # 分离标题和内容
            title_parts = re.split(r'[。！？]', title_text, 1)
            if len(title_parts) > 1 and title_parts[1].strip():
                point_buffer = [num, title_parts[0] + '。', title_parts[1].strip()]
            else:
                point_buffer = [num, title_text]
        else:
            if found_first_point and point_buffer:
                if not line.startswith('#'):
                    if len(point_buffer) == 2:
                        point_buffer.append(line)
                    else:
                        point_buffer[-1] += ' ' + line
            elif not found_first_point:
                if line.startswith('> '):
                    result['intro'] = line[2:].strip()
                elif not line.startswith('#') and not re.search(youtube_pattern, line):
                    intro_lines.append(line)
    
    if point_buffer:
        result['points'].append({
            'number': point_buffer[0],
            'title': point_buffer[1],
            'content': ' '.join(point_buffer[2:]) if len(point_buffer) > 2 else ''
        })
    
    if not result['intro'] and intro_lines:
        result['intro'] = ' '.join([l for l in intro_lines if not l.startswith('这期播客')][:2])
    
    return result


def process_markdown_text(text: str) -> str:
    """处理 Markdown 格式"""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def generate_html_content(data: dict, page_num: int = 0, total_pages: int = 1, 
                          cover_image_url: str = None, show_intro: bool = False,
                          is_last_page: bool = False) -> str:
    """生成 HTML 内容"""
    html_parts = []
    
    has_cover = cover_image_url and page_num == 0
    
    if page_num == 0:
        if data['title']:
            title = process_markdown_text(data['title'])
            html_parts.append(f"<h1>{title}</h1>")
        
        if show_intro and data['intro']:
            intro = process_markdown_text(data['intro'])
            html_parts.append(f'<div class="intro">{intro}</div>')
        
        html_parts.append('<div class="transition">▼ 核心观点</div>')
    else:
        # 续页使用短标题
        if data['short_title']:
            short_title = process_markdown_text(data['short_title'])
            html_parts.append(f"<h2>{short_title}（续）</h2>")
    
    html_parts.append('<div class="points-container">')
    
    for point in data['points']:
        title_html = process_markdown_text(point['title'])
        content_html = ''
        if point.get('content'):
            content_html = f'<div class="point-content">{process_markdown_text(point["content"])}</div>'
        
        html_parts.append(f'''
        <div class="point">
            <div class="point-header">
                <span class="point-number">{point["number"]}.</span>
                <span class="point-title">{title_html}</span>
            </div>
            {content_html}
        </div>
        ''')
    
    html_parts.append('</div>')
    
    content = '\n'.join(html_parts)
    
    return get_html_template(content, page_num, total_pages, 
                            cover_image_url if page_num == 0 else None,
                            is_last_page)


async def get_youtube_thumbnail(youtube_url: str) -> str:
    """获取 YouTube 封面图"""
    if not youtube_url:
        return None
    
    patterns = [
        r'youtube\.com/watch\?v=([\w-]+)',
        r'youtu\.be/([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return f"https://img.youtube.com/vi/{match.group(1)}/maxresdefault.jpg"
    
    return None


async def render_to_image(html_content: str, output_path: str):
    """渲染为图片 - 自适应内容高度"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome')
        page = await browser.new_page(viewport={'width': CARD_WIDTH, 'height': CARD_HEIGHT})
        
        await page.set_content(html_content)
        await page.wait_for_timeout(1500)
        
        # 获取实际内容高度
        body_height = await page.evaluate('document.body.scrollHeight')
        
        # 确保最小高度为 CARD_HEIGHT，但如果内容更多则扩展
        actual_height = max(CARD_HEIGHT, body_height)
        
        # 重新设置视口并截图
        await page.set_viewport_size({'width': CARD_WIDTH, 'height': actual_height})
        await page.wait_for_timeout(300)
        
        await page.screenshot(path=output_path, clip={
            'x': 0, 'y': 0,
            'width': CARD_WIDTH, 'height': actual_height
        })
        
        await browser.close()
        
        return actual_height


def get_output_dir(md_file: str, base_dir: str = None) -> Path:
    """生成输出目录"""
    if base_dir is None:
        base_dir = '/Users/ugreen/Documents/obsidian/attachments'
    
    filename = Path(md_file).stem
    match = re.match(r'^(\d{4})-(.+)$', filename)
    if match:
        date_str = match.group(1)
        title = match.group(2)
    else:
        date_str = datetime.now().strftime('%m%d')
        title = filename
    
    title = re.sub(r'[<>:"/\\|?*]', '-', title)
    output_dir = Path(base_dir) / f"{date_str}-{title}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


async def convert_md_to_images(md_file: str, output_dir: str = None, 
                                points_per_page: int = 4,
                                with_cover: bool = True) -> list:
    """转换 Markdown 为图片"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = parse_content_to_points(content)
    
    if not data['points']:
        print("警告：未能解析出核心观点")
        return []
    
    # YouTube 封面图
    cover_url = None
    if with_cover and data['youtube_url']:
        cover_url = await get_youtube_thumbnail(data['youtube_url'])
        if cover_url:
            print(f"📷 检测到 YouTube 链接，使用视频封面")
    
    # 智能分页（字体放大后每页观点数减少）
    has_intro = bool(data['intro'])
    total_points = len(data['points'])
    
    if cover_url:
        first_page_capacity = 2  # 有封面图时首页只放2个观点
    else:
        first_page_capacity = 2 if has_intro else points_per_page
    
    if total_points <= first_page_capacity:
        total_pages = 1
        page_distribution = [total_points]
    else:
        remaining = total_points - first_page_capacity
        extra_pages = (remaining + points_per_page - 1) // points_per_page
        total_pages = 1 + extra_pages
        
        if extra_pages == 1:
            page_distribution = [first_page_capacity, remaining]
        else:
            base_per_page = remaining // extra_pages
            extra_points = remaining % extra_pages
            
            page_distribution = [first_page_capacity]
            for i in range(extra_pages):
                points = base_per_page + (1 if i < extra_points else 0)
                page_distribution.append(points)
    
    if output_dir is None:
        output_dir = get_output_dir(md_file)
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    output_files = []
    current_point = 0
    
    print(f"📊 分页方案: {page_distribution} (共 {total_points} 个观点)")
    
    for page_num in range(total_pages):
        page_points = page_distribution[page_num]
        is_last_page = (page_num == total_pages - 1)
        
        page_data = {
            'title': data['title'],
            'short_title': data['short_title'],
            'intro': data['intro'],
            'points': data['points'][current_point:current_point + page_points]
        }
        
        for i, point in enumerate(page_data['points']):
            point['number'] = str(current_point + i + 1)
        
        html_content = generate_html_content(
            page_data, page_num, total_pages,
            cover_url if page_num == 0 else None,
            show_intro=(page_num == 0 and has_intro),
            is_last_page=is_last_page
        )
        
        output_path = output_dir / f'page-{page_num + 1}.png'
        actual_height = await render_to_image(html_content, str(output_path))
        output_files.append(str(output_path))
        
        height_note = f" (高度: {actual_height}px)" if actual_height > CARD_HEIGHT else ""
        print(f"✅ 生成第 {page_num + 1}/{total_pages} 页: {output_path}{height_note}")
        
        current_point += page_points
    
    return output_files


def main():
    parser = argparse.ArgumentParser(description='Markdown 转知识卡片')
    parser.add_argument('input', help='Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-p', '--points-per-page', type=int, default=4,
                        help='每页观点数（默认: 4）')
    parser.add_argument('--no-cover', action='store_true', help='不使用封面图')
    parser.add_argument('--author', help='水印作者')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误：文件不存在: {args.input}")
        return 1
    
    global WATERMARK_AUTHOR
    if args.author:
        WATERMARK_AUTHOR = args.author
    
    output_files = asyncio.run(convert_md_to_images(
        args.input,
        args.output,
        args.points_per_page,
        not args.no_cover
    ))
    
    if output_files:
        print(f"\n🎉 完成！共生成 {len(output_files)} 张图片")
        print(f"📁 保存目录: {Path(output_files[0]).parent}")
    
    return 0


if __name__ == '__main__':
    exit(main())
