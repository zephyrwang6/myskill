#!/usr/bin/env python3
"""
Markdown to Image Converter - Premium Poster Edition

将 Markdown 内容转换为精美的多页图片海报，适合社交媒体分享。
- 自适应布局，减少留白
- 大字体 + 宽字间距 + 宽行间距
- 支持 AI 生成的头图
"""

import argparse
import asyncio
import os
import re
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    print("请安装 markdown: pip3 install markdown")
    sys.exit(1)

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("请安装 playwright: pip3 install playwright && playwright install chromium")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("请安装 requests: pip3 install requests")
    sys.exit(1)


def extract_video_id(youtube_url: str) -> str | None:
    """从 YouTube URL 提取视频 ID"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None


def get_youtube_thumbnail(youtube_url: str) -> str | None:
    """获取 YouTube 视频封面 URL"""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return None
    
    try:
        resp = requests.get(f"https://noembed.com/embed?url={youtube_url}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            thumb = data.get('thumbnail_url')
            if thumb:
                return thumb
    except Exception as e:
        print(f"   noembed 失败: {e}")
    
    resolutions = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault']
    for res in resolutions:
        url = f"https://i.ytimg.com/vi/{video_id}/{res}.jpg"
        try:
            resp = requests.head(url, timeout=5)
            content_length = int(resp.headers.get('content-length', 0))
            if resp.status_code == 200 and content_length > 2000:
                return url
        except:
            continue
    
    return None


def download_file(url: str, save_path: str) -> str | None:
    """下载文件到本地"""
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return save_path
    except Exception as e:
        print(f"⚠️ 下载失败: {e}")
    return None


def process_markdown_for_display(md_content: str) -> tuple[str, str, str, str, str, list[str]]:
    """预处理 Markdown 内容，提取嘉宾、主题等信息"""
    lines = md_content.split('\n')
    original_title = ""
    guest = ""
    topic = ""
    meta_info = ""
    content_items = []
    current_item = []
    intro_lines = []
    
    # 解析状态标记
    found_title = False
    found_first_item = False
    stop_processing = False
    
    for line in lines:
        stripped_line = line.strip()
        
        # 0. 停止处理标志
        if stripped_line == '---' or stripped_line.startswith('# 精华片段') or (stripped_line.startswith('## ') and '短版' not in line):
            if found_first_item:
                stop_processing = True
                break
        
        # 1. 提取标题
        if line.startswith('# ') and not found_title:
            original_title = line[2:].strip()
            found_title = True
            continue
        
        # 2. 尝试提取列表项 (支持 "1、" 或 "1." 格式)
        list_match = re.match(r'^(\d+)[、.]\s*', line)
        
        if list_match:
            found_first_item = True
            # 保存上一个条目
            if current_item:
                content_items.append('\n'.join(current_item))
            current_item = [line]
            continue
            
        # 3. 处理列表项内容的延续
        if found_first_item and current_item:
            if stripped_line: # 非空行追加
                current_item.append(line)
            # 空行忽略，或者是条目间的分隔
            continue
            
        # 4. 提取元信息 (引用块)
        if line.startswith('> '):
            line_content = line[2:].strip()
            line_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', line_content)
            
            if '嘉宾' in line_content:
                guest_match = re.search(r'嘉宾[:：]\s*(.+)', line_content)
                if guest_match:
                    guest = guest_match.group(1).strip()
            elif '主题' in line_content:
                topic_match = re.search(r'主题[:：]\s*(.+)', line_content)
                if topic_match:
                    topic = topic_match.group(1).strip()
            
            meta_info += line_content + " | "
            continue
            
        # 5. 提取介绍文字 (标题后，列表前)
        if found_title and not found_first_item:
            # 跳过特定标记行
            if '📱' in line or '短版' in line:
                continue
            
            if stripped_line:
                # 移除 markdown 加粗标记
                clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', stripped_line)
                intro_lines.append(clean_line)
    
    # 循环结束，保存最后一个条目
    if current_item:
        content_items.append('\n'.join(current_item))
    
    meta_info = meta_info.rstrip(' | ')
    intro_text = '\n'.join(intro_lines)
    
    # 构建显示标题：嘉宾：主题
    display_title = original_title
    
    # 尝试从标题中解析嘉宾和主题 (格式 # MMDD：嘉宾 X 栏目：观点)
    # 示例: # 0128：Lucas Crespo X Every Think Week：让 Claude 学会设计师的审美直觉
    if "：" in original_title or ": " in original_title:
        parts = re.split(r'[:：]', original_title)
        if len(parts) >= 3:
            # 尝试识别嘉宾和主题
            # 简单策略：取最后一部分作为主题（观点），中间部分作为嘉宾/栏目
            topic = parts[-1].strip()
            guest_section = parts[-2].strip()
            
            # 如果没有显式提取到嘉宾，尝试从标题中间部分获取
            if not guest:
                guest = guest_section
            
            # 如果标题很长，使用缩短的显示标题
            if len(topic) > 10:
                display_title = f"{guest}：{topic}"
    
    return display_title, guest, topic, meta_info, intro_text, content_items


def convert_item_to_html(item: str, index: int) -> str:
    """将单个条目转换为 HTML"""
    item = re.sub(r'^(\d+)[、.]\s*', '', item.strip())
    item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
    item = re.sub(r'"([^"]+)"', r'<span class="quote">"\1"</span>', item)
    
    return f'''
    <div class="item">
        <div class="item-number">{index}</div>
        <div class="item-content">{item}</div>
    </div>
    '''


def generate_topic_svg(topic: str) -> str:
    """根据主题生成相应的 SVG 装饰图"""
    topic_lower = topic.lower() if topic else ""
    
    # AI/AGI 相关主题
    if 'agi' in topic_lower or '通用' in topic or 'ai' in topic_lower:
        return '''
        <svg viewBox="0 0 800 120" class="header-icon">
            <!-- 神经网络节点 -->
            <g class="network">
                <!-- 左侧输入层 -->
                <circle cx="80" cy="30" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="80" cy="60" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="80" cy="90" r="12" fill="none" stroke="#333" stroke-width="2"/>
                
                <!-- 中间隐藏层 -->
                <circle cx="180" cy="35" r="14" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="180" cy="75" r="14" fill="none" stroke="#333" stroke-width="2"/>
                
                <!-- 连接线 -->
                <line x1="92" y1="30" x2="166" y2="35" stroke="#aaa" stroke-width="1.5"/>
                <line x1="92" y1="30" x2="166" y2="75" stroke="#aaa" stroke-width="1.5"/>
                <line x1="92" y1="60" x2="166" y2="35" stroke="#aaa" stroke-width="1.5"/>
                <line x1="92" y1="60" x2="166" y2="75" stroke="#aaa" stroke-width="1.5"/>
                <line x1="92" y1="90" x2="166" y2="35" stroke="#aaa" stroke-width="1.5"/>
                <line x1="92" y1="90" x2="166" y2="75" stroke="#aaa" stroke-width="1.5"/>
                
                <!-- 输出节点 -->
                <circle cx="280" cy="55" r="16" fill="none" stroke="#333" stroke-width="2.5"/>
                <line x1="194" y1="35" x2="264" y2="55" stroke="#aaa" stroke-width="1.5"/>
                <line x1="194" y1="75" x2="264" y2="55" stroke="#aaa" stroke-width="1.5"/>
            </g>
            
            <!-- 虚线连接 -->
            <line x1="320" y1="55" x2="480" y2="55" stroke="#333" stroke-width="2" stroke-dasharray="8,6"/>
            
            <!-- 大脑图标 -->
            <g transform="translate(500, 15)">
                <ellipse cx="60" cy="40" rx="50" ry="38" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M30 35 Q45 20 60 30 Q75 20 90 35" fill="none" stroke="#333" stroke-width="1.5"/>
                <path d="M25 50 Q40 40 55 50 Q70 40 95 50" fill="none" stroke="#333" stroke-width="1.5"/>
                <path d="M35 65 Q50 55 65 65 Q80 55 85 65" fill="none" stroke="#333" stroke-width="1.5"/>
            </g>
            
            <!-- 右侧对话泡 -->
            <g transform="translate(650, 25)">
                <rect x="0" y="0" width="70" height="50" rx="10" fill="none" stroke="#333" stroke-width="2"/>
                <polygon points="20,50 35,70 50,50" fill="none" stroke="#333" stroke-width="2"/>
                <line x1="15" y1="18" x2="55" y2="18" stroke="#333" stroke-width="1.5"/>
                <line x1="15" y1="32" x2="45" y2="32" stroke="#333" stroke-width="1.5"/>
            </g>
        </svg>
        <div class="header-text">AI × Human Dialogue</div>
        '''
    
    # 开源相关主题
    elif '开源' in topic or 'open' in topic_lower:
        return '''
        <svg viewBox="0 0 800 120" class="header-icon">
            <!-- 开源符号 -->
            <g transform="translate(150, 10)">
                <circle cx="50" cy="50" r="35" fill="none" stroke="#333" stroke-width="2.5"/>
                <circle cx="50" cy="50" r="15" fill="none" stroke="#333" stroke-width="2"/>
            </g>
            
            <!-- 虚线 -->
            <line x1="260" y1="60" x2="400" y2="60" stroke="#333" stroke-width="2" stroke-dasharray="8,6"/>
            
            <!-- 代码括号 -->
            <g transform="translate(420, 20)">
                <path d="M30 0 L0 40 L30 80" fill="none" stroke="#333" stroke-width="3"/>
                <path d="M70 0 L100 40 L70 80" fill="none" stroke="#333" stroke-width="3"/>
                <line x1="35" y1="60" x2="65" y2="20" stroke="#333" stroke-width="2"/>
            </g>
            
            <!-- 虚线 -->
            <line x1="540" y1="60" x2="620" y2="60" stroke="#333" stroke-width="2" stroke-dasharray="8,6"/>
            
            <!-- 分享图标 -->
            <g transform="translate(640, 20)">
                <circle cx="20" cy="15" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="60" cy="40" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <circle cx="20" cy="65" r="12" fill="none" stroke="#333" stroke-width="2"/>
                <line x1="30" y1="20" x2="50" y2="35" stroke="#333" stroke-width="2"/>
                <line x1="30" y1="60" x2="50" y2="45" stroke="#333" stroke-width="2"/>
            </g>
        </svg>
        <div class="header-text">Open Source × Innovation</div>
        '''
    
    # 默认 - 对话/播客主题
    else:
        return '''
        <svg viewBox="0 0 800 120" class="header-icon">
            <!-- 麦克风 -->
            <g transform="translate(100, 15)">
                <rect x="20" y="0" width="40" height="60" rx="20" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M0 45 L0 55 Q0 85 40 85 Q80 85 80 55 L80 45" fill="none" stroke="#333" stroke-width="2"/>
                <line x1="40" y1="85" x2="40" y2="100" stroke="#333" stroke-width="2"/>
                <line x1="20" y1="100" x2="60" y2="100" stroke="#333" stroke-width="2"/>
            </g>
            
            <!-- 声波 -->
            <g transform="translate(200, 30)">
                <path d="M0 30 Q10 0 20 30 Q30 60 40 30" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M50 30 Q60 10 70 30 Q80 50 90 30" fill="none" stroke="#333" stroke-width="2"/>
            </g>
            
            <!-- 虚线 -->
            <line x1="320" y1="55" x2="480" y2="55" stroke="#333" stroke-width="2" stroke-dasharray="8,6"/>
            
            <!-- 两个人头轮廓 -->
            <g transform="translate(500, 15)">
                <circle cx="30" cy="25" r="18" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M5 90 Q5 55 30 55 Q55 55 55 90" fill="none" stroke="#333" stroke-width="2"/>
            </g>
            <g transform="translate(580, 15)">
                <circle cx="30" cy="25" r="18" fill="none" stroke="#333" stroke-width="2"/>
                <path d="M5 90 Q5 55 30 55 Q55 55 55 90" fill="none" stroke="#333" stroke-width="2"/>
            </g>
            
            <!-- 对话气泡 -->
            <g transform="translate(700, 20)">
                <ellipse cx="40" cy="30" rx="35" ry="25" fill="none" stroke="#333" stroke-width="2"/>
                <polygon points="25,50 15,70 45,55" fill="none" stroke="#333" stroke-width="2"/>
            </g>
        </svg>
        <div class="header-text">Deep Dialogue</div>
        '''

def generate_page_html(
    items_html: str,
    title: str = "",
    topic: str = "",
    meta_info: str = "",
    intro_text: str = "",
    page_num: int = 1,
    total_pages: int = 1,
    width: int = 1080,
    is_first_page: bool = True,
    item_count: int = 5,
) -> str:
    """生成单页 HTML - 优化版海报排版"""
    
    height = int(width * 4 / 3)
    
    # 根据主题生成装饰性 SVG header
    header_html = ""
    if is_first_page:
        # 判断主题关键词生成相应图标
        svg_content = generate_topic_svg(topic)
        header_html = f'''
        <div class="header-banner">
            {svg_content}
        </div>
        '''
    
    title_html = f'<h1 class="title">{title}</h1>' if title and is_first_page else ""
    meta_html = f'<div class="meta-info">{meta_info}</div>' if meta_info and is_first_page else ""
    intro_html = f'<p class="intro">{intro_text}</p>' if intro_text and is_first_page else ""
    page_indicator = f'<div class="page-indicator">{page_num} / {total_pages}</div>' if total_pages > 1 else ""
    
    # 根据条目数量动态调整字体大小
    base_font_size = 32
    if item_count <= 3:
        base_font_size = 38
    elif item_count <= 4:
        base_font_size = 35
    elif item_count <= 5:
        base_font_size = 32
    elif item_count <= 6:
        base_font_size = 30
    else:
        base_font_size = 28
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700;900&display=swap');
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        html, body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
        }}
        
        body {{
            font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #ffffff;
            color: #1a1a1a;
        }}
        
        .container {{
            width: 100%;
            height: 100%;
            padding: 48px 52px;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        
        /* 装饰性横幅 */
        .header-banner {{
            width: 100%;
            height: 140px;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #fafafa;
            border-radius: 12px;
        }}
        
        .header-icon {{
            width: 600px;
            height: 100px;
        }}
        
        .header-text {{
            font-size: 18px;
            color: #666;
            letter-spacing: 3px;
            margin-top: 8px;
            font-weight: 500;
        }}
        
        /* 标题 - 超大字体 */
        .title {{
            font-size: 52px;
            font-weight: 900;
            color: #1a1a1a;
            margin-bottom: 16px;
            line-height: 1.15;
            letter-spacing: 2px;
        }}
        
        /* 元信息 */
        .meta-info {{
            font-size: 18px;
            color: #999999;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid #f0f0f0;
            letter-spacing: 1px;
        }}
        
        /* 介绍文字 */
        .intro {{
            font-size: 30px;
            color: #e74c3c;
            font-weight: 700;
            margin-bottom: 32px;
            line-height: 1.5;
            letter-spacing: 1px;
        }}
        
        /* 内容区域 - 自适应填充 */
        .content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 0;
        }}
        
        /* 单个条目 */
        .item {{
            display: flex;
            align-items: flex-start;
            gap: 24px;
            flex: 1;
            padding: 16px 0;
        }}
        
        .item-number {{
            flex-shrink: 0;
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: #fff;
            border-radius: 50%;
            font-size: 24px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
        }}
        
        .item-content {{
            flex: 1;
            font-size: {base_font_size}px;
            color: #2c2c2c;
            line-height: 1.7;
            letter-spacing: 1.5px;
        }}
        
        .item-content strong {{
            color: #e74c3c;
            font-weight: 700;
        }}
        
        .item-content .quote {{
            color: #2980b9;
            font-weight: 600;
        }}
        
        /* 页码指示器 */
        .page-indicator {{
            position: absolute;
            bottom: 28px;
            right: 52px;
            font-size: 20px;
            color: #cccccc;
            font-weight: 600;
            letter-spacing: 2px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {header_html}
        {title_html}
        {meta_html}
        {intro_html}
        <div class="content">
            {items_html}
        </div>
        {page_indicator}
    </div>
</body>
</html>'''
    
    return html


async def render_html_to_image(html_content: str, output_path: str, width: int = 1080) -> str:
    """使用 Playwright 将 HTML 渲染为图片"""
    height = int(width * 4 / 3)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        
        await page.set_content(html_content)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        await page.screenshot(path=output_path, type="png")
        await browser.close()
    
    return output_path


async def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 转换为精美的多页图片海报"
    )
    parser.add_argument("--file", "-f", required=True, help="Markdown 文件路径")
    parser.add_argument("--output-dir", "-o", help="输出目录（默认: attachments/MMDD）")
    parser.add_argument("--youtube", "-y", help="YouTube 视频链接")
    parser.add_argument("--header-image", "-i", help="自定义头图路径（16:9 手绘风格）")
    parser.add_argument("--width", "-w", type=int, default=1080)
    parser.add_argument("--items-per-page", type=int, default=5, help="每页显示条目数（默认5）")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        today = datetime.now().strftime("%m%d")
        output_dir = file_path.parent / "attachments" / today
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    title, guest, topic, meta_info, intro_text, content_items = process_markdown_for_display(md_content)
    print(f"📄 标题: {title}")
    if topic:
        print(f"📌 主题: {topic}")
    print(f"📝 共 {len(content_items)} 个条目")
    
    # 计算分页
    items_per_page_first = args.items_per_page
    items_per_page_rest = args.items_per_page + 2
    
    first_page_items = content_items[:items_per_page_first]
    remaining_items = content_items[items_per_page_first:]
    
    total_pages = 1
    if remaining_items:
        total_pages += (len(remaining_items) + items_per_page_rest - 1) // items_per_page_rest
    
    print(f"📑 将生成 {total_pages} 页图片")
    
    output_paths = []
    item_index = 1
    
    # 第一页
    items_html = ""
    for item in first_page_items:
        items_html += convert_item_to_html(item, item_index)
        item_index += 1
    
    html = generate_page_html(
        items_html=items_html,
        title=title,
        topic=topic,
        meta_info=meta_info,
        intro_text=intro_text,
        page_num=1,
        total_pages=total_pages,
        width=args.width,
        is_first_page=True,
        item_count=len(first_page_items),
    )
    
    output_path = output_dir / f"page_1.png"
    print(f"🎨 渲染第 1 页...")
    await render_html_to_image(html, str(output_path), args.width)
    output_paths.append(output_path)
    
    # 后续页
    current_page = 2
    for i in range(0, len(remaining_items), items_per_page_rest):
        page_items = remaining_items[i:i + items_per_page_rest]
        
        items_html = ""
        for item in page_items:
            items_html += convert_item_to_html(item, item_index)
            item_index += 1
        
        html = generate_page_html(
            items_html=items_html,
            title=title,
            page_num=current_page,
            total_pages=total_pages,
            width=args.width,
            is_first_page=False,
            item_count=len(page_items),
        )
        
        output_path = output_dir / f"page_{current_page}.png"
        print(f"🎨 渲染第 {current_page} 页...")
        await render_html_to_image(html, str(output_path), args.width)
        output_paths.append(output_path)
        current_page += 1
    
    print(f"\n✅ 完成！共生成 {len(output_paths)} 张图片：")
    for p in output_paths:
        print(f"   📷 {p}")
    
    return output_paths


if __name__ == "__main__":
    asyncio.run(main())
