#!/usr/bin/env python3
"""
获取飞书知识库目录结构
用法: python list_wiki.py [--json]
"""

import os
import requests
import json
import argparse

# 飞书应用配置
APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a9f6d47ef9fa5cd5")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
BASE_URL = "https://open.feishu.cn/open-apis"

# 知识库根节点
ROOT_NODE = "YylJw806IinEJmkwOWVcv8HInph"


def get_token():
    """获取 tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    return response.json().get("tenant_access_token")


def get_node_info(token, node_token):
    """获取节点信息"""
    url = f"{BASE_URL}/wiki/v2/spaces/get_node?token={node_token}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    result = response.json()
    if result.get("code") == 0:
        return result["data"]["node"]
    return None


def get_children(token, space_id, parent_token):
    """获取子节点列表"""
    url = f"{BASE_URL}/wiki/v2/spaces/{space_id}/nodes?parent_node_token={parent_token}&page_size=50"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    result = response.json()
    if result.get("code") == 0:
        return result.get("data", {}).get("items", [])
    return []


def build_tree(token, node_token, max_depth=2, current_depth=0):
    """递归构建目录树"""
    node = get_node_info(token, node_token)
    if not node:
        return None
    
    tree = {
        "title": node["title"],
        "token": node["node_token"],
        "type": node.get("obj_type", "unknown"),
        "children": []
    }
    
    if current_depth < max_depth and node.get("has_child"):
        children = get_children(token, node["space_id"], node["node_token"])
        for child in children:
            child_tree = build_tree(token, child["node_token"], max_depth, current_depth + 1)
            if child_tree:
                tree["children"].append(child_tree)
    
    return tree


def print_tree(tree, indent=0):
    """打印目录树"""
    prefix = "  " * indent
    marker = "📁" if tree["children"] else "📄"
    print(f"{prefix}{marker} {tree['title']} ({tree['token']})")
    for child in tree["children"]:
        print_tree(child, indent + 1)


def main():
    parser = argparse.ArgumentParser(description="获取飞书知识库目录结构")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--depth", type=int, default=2, help="目录深度 (默认: 2)")
    args = parser.parse_args()
    
    token = get_token()
    tree = build_tree(token, ROOT_NODE, max_depth=args.depth)
    
    if args.json:
        print(json.dumps(tree, ensure_ascii=False, indent=2))
    else:
        print("飞书知识库目录结构:")
        print("-" * 40)
        print_tree(tree)


if __name__ == "__main__":
    main()
