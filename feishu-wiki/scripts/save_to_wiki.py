#!/usr/bin/env python3
"""
保存文档到飞书知识库
用法:
    python save_to_wiki.py --title "文档标题" --content "文档内容"
    python save_to_wiki.py --file /path/to/markdown.md
    python save_to_wiki.py --file /path/to/markdown.md --parent TOKEN
"""

import os
import requests
import json
import argparse
import re
from pathlib import Path

# 飞书应用配置
APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a9f6d47ef9fa5cd5")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
BASE_URL = "https://open.feishu.cn/open-apis"

# 知识库配置
WIKI_SPACE_ID = "7591325128043121630"
DEFAULT_PARENT_NODE = "YylJw806IinEJmkwOWVcv8HInph"  # 草稿箱


def get_token():
    """获取 tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    raise Exception(f"获取 token 失败: {result}")


def strip_markdown_formatting(text):
    """移除 Markdown 格式标记"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text


def markdown_to_feishu_blocks(content):
    """将 Markdown 转换为飞书文档 blocks"""
    blocks = []
    lines = content.split('\n')
    current_paragraph = []
    in_frontmatter = False
    
    def flush_paragraph():
        nonlocal current_paragraph
        if current_paragraph:
            text = '\n'.join(current_paragraph).strip()
            text = strip_markdown_formatting(text)
            if text:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"text_run": {"content": text, "text_element_style": {}}}],
                        "style": {}
                    }
                })
            current_paragraph = []
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if i == 0:
                in_frontmatter = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue
        
        if in_frontmatter:
            continue
        
        if re.match(r'^# [^#]', line):
            flush_paragraph()
            blocks.append({
                "block_type": 3,
                "heading1": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(line[2:].strip()), "text_element_style": {}}}],
                    "style": {}
                }
            })
        elif re.match(r'^## [^#]', line):
            flush_paragraph()
            blocks.append({
                "block_type": 4,
                "heading2": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(line[3:].strip()), "text_element_style": {}}}],
                    "style": {}
                }
            })
        elif re.match(r'^### [^#]', line):
            flush_paragraph()
            blocks.append({
                "block_type": 5,
                "heading3": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(line[4:].strip()), "text_element_style": {}}}],
                    "style": {}
                }
            })
        elif re.match(r'^#### ', line):
            flush_paragraph()
            blocks.append({
                "block_type": 6,
                "heading4": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(line[5:].strip()), "text_element_style": {}}}],
                    "style": {}
                }
            })
        elif line.strip() == '':
            flush_paragraph()
        elif line.startswith('- ') or line.startswith('* '):
            flush_paragraph()
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(line[2:].strip()), "text_element_style": {}}}],
                    "style": {}
                }
            })
        elif re.match(r'^\d+\. ', line):
            flush_paragraph()
            content_text = re.sub(r'^\d+\. ', '', line).strip()
            blocks.append({
                "block_type": 13,
                "ordered": {
                    "elements": [{"text_run": {"content": strip_markdown_formatting(content_text), "text_element_style": {}}}],
                    "style": {}
                }
            })
        else:
            current_paragraph.append(line)
    
    flush_paragraph()
    return blocks


def create_wiki_node(token, title, parent_node=None):
    """创建知识库文档节点"""
    url = f"{BASE_URL}/wiki/v2/spaces/{WIKI_SPACE_ID}/nodes"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "obj_type": "docx",
        "node_type": "origin",
        "title": title,
        "parent_node_token": parent_node or DEFAULT_PARENT_NODE,
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    if result.get("code") == 0:
        node = result["data"]["node"]
        return node["node_token"], node["obj_token"]
    raise Exception(f"创建文档失败: {result}")


def write_content(token, document_id, content):
    """写入文档内容"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    blocks = markdown_to_feishu_blocks(content)
    
    if not blocks:
        return True
    
    batch_size = 50
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{document_id}/children"
        payload = {"children": batch, "index": -1}
        
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"写入失败: {result}")
            return False
    
    return True


def save_to_wiki(title, content, parent_node=None):
    """保存文档到飞书知识库"""
    token = get_token()
    
    node_token, obj_token = create_wiki_node(token, title, parent_node)
    success = write_content(token, obj_token, content)
    
    doc_url = f"https://my.feishu.cn/wiki/{node_token}"
    
    if success:
        print(f"✅ 文档保存成功!")
        print(f"📄 标题: {title}")
        print(f"🔗 地址: {doc_url}")
    else:
        print(f"⚠️ 文档创建成功但内容写入可能不完整")
        print(f"🔗 地址: {doc_url}")
    
    return doc_url


def main():
    parser = argparse.ArgumentParser(description="保存文档到飞书知识库")
    parser.add_argument("--title", "-t", help="文档标题")
    parser.add_argument("--content", "-c", help="文档内容")
    parser.add_argument("--file", "-f", help="Markdown 文件路径")
    parser.add_argument("--parent", "-p", help="父节点 token")
    
    args = parser.parse_args()
    
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"文件不存在: {args.file}")
            return
        
        content = path.read_text(encoding="utf-8")
        title = args.title
        if not title:
            # 使用文件名作为标题（保留日期前缀）
            title = path.stem
        
        save_to_wiki(title, content, args.parent)
    
    elif args.title and args.content:
        save_to_wiki(args.title, args.content, args.parent)
    
    else:
        print("用法:")
        print("  python save_to_wiki.py --file /path/to/document.md")
        print("  python save_to_wiki.py --title \"标题\" --content \"内容\"")
        print("  python save_to_wiki.py --file doc.md --parent TOKEN")


if __name__ == "__main__":
    main()
