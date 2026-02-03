#!/usr/bin/env python3
"""
读取飞书多维表格内容
用法:
    python read_bitable.py --url "https://my.feishu.cn/wiki/xxx?table=xxx&view=xxx"
    python read_bitable.py --app-token xxx --table-id xxx
"""
from __future__ import annotations

import requests
import json
import argparse
import re
from urllib.parse import urlparse, parse_qs

# 飞书应用配置
APP_ID = "cli_a9f6d47ef9fa5cd5"
APP_SECRET = "REMOVED_FEISHU_SECRET"
BASE_URL = "https://open.feishu.cn/open-apis"


def get_token():
    """获取 tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    raise Exception(f"获取 token 失败: {result}")


def parse_feishu_url(url: str) -> tuple[str, str, str]:
    """解析飞书 URL，提取 app_token, table_id, view_id"""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # 从 URL 路径提取 wiki token 或 base token
    path_parts = parsed.path.strip('/').split('/')
    
    app_token = None
    table_id = query.get('table', [None])[0]
    view_id = query.get('view', [None])[0]
    
    # 尝试识别不同格式的 URL
    if 'wiki' in path_parts:
        idx = path_parts.index('wiki')
        if idx + 1 < len(path_parts):
            app_token = path_parts[idx + 1]
    elif 'base' in path_parts:
        idx = path_parts.index('base')
        if idx + 1 < len(path_parts):
            app_token = path_parts[idx + 1]
    else:
        # 可能直接是 token
        app_token = path_parts[-1] if path_parts else None
    
    return app_token, table_id, view_id


def get_wiki_node_info(token: str, wiki_token: str) -> dict:
    """获取知识库节点信息，找到关联的 Bitable app_token"""
    url = f"{BASE_URL}/wiki/v2/spaces/get_node"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"token": wiki_token}
    
    response = requests.get(url, headers=headers, params=params)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("node", {})
    return {}


def list_tables(token: str, app_token: str) -> list:
    """列出 Bitable 中的所有表"""
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("items", [])
    print(f"⚠️ 列出表格失败: {result}")
    return []


def get_table_fields(token: str, app_token: str, table_id: str) -> list:
    """获取表格字段定义"""
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("items", [])
    return []


def get_table_records(token: str, app_token: str, table_id: str, view_id: str = None, page_size: int = 100) -> list:
    """获取表格记录"""
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": page_size}
    if view_id:
        params["view_id"] = view_id
    
    all_records = []
    page_token = None
    
    while True:
        if page_token:
            params["page_token"] = page_token
        
        response = requests.get(url, headers=headers, params=params)
        result = response.json()
        
        if result.get("code") != 0:
            print(f"⚠️ 获取记录失败: {result}")
            break
        
        data = result.get("data", {})
        records = data.get("items", [])
        all_records.extend(records)
        
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")
    
    return all_records


def format_field_value(value, field_type: int) -> str:
    """格式化字段值"""
    if value is None:
        return ""
    
    # 文本类型
    if field_type == 1:
        if isinstance(value, list):
            return "".join([v.get("text", "") if isinstance(v, dict) else str(v) for v in value])
        return str(value)
    
    # 数字类型
    if field_type == 2:
        return str(value)
    
    # 单选
    if field_type == 3:
        return value if isinstance(value, str) else str(value)
    
    # 多选
    if field_type == 4:
        if isinstance(value, list):
            return ", ".join(value)
        return str(value)
    
    # 日期
    if field_type == 5:
        return str(value)
    
    # 复选框
    if field_type == 7:
        return "✓" if value else "✗"
    
    # 人员
    if field_type == 11:
        if isinstance(value, list):
            return ", ".join([p.get("name", p.get("id", "")) for p in value if isinstance(p, dict)])
        return str(value)
    
    # URL
    if field_type == 15:
        if isinstance(value, dict):
            return value.get("link", value.get("text", str(value)))
        return str(value)
    
    # 默认处理
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return ", ".join([str(v) for v in value])
    return str(value)


def get_bitable_token_from_wiki(token: str, wiki_token: str) -> str:
    """从知识库节点获取关联的 Bitable app_token"""
    # 方法1: 尝试获取节点信息
    url = f"{BASE_URL}/wiki/v2/spaces/get_node"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"token": wiki_token}
    
    response = requests.get(url, headers=headers, params=params)
    result = response.json()
    
    if result.get("code") == 0:
        node = result.get("data", {}).get("node", {})
        obj_token = node.get("obj_token")
        obj_type = node.get("obj_type")
        print(f"📄 节点类型: {obj_type}")
        print(f"📄 Obj Token: {obj_token}")
        if obj_type == "bitable":
            return obj_token
        # 如果是 docx，可能内嵌了 bitable
        return obj_token
    
    print(f"⚠️ 获取节点信息失败: {result}")
    return wiki_token


def read_bitable(url: str = None, app_token: str = None, table_id: str = None, view_id: str = None):
    """读取飞书多维表格"""
    token = get_token()
    
    # 解析 URL
    wiki_token = None
    if url:
        parsed_app_token, parsed_table_id, parsed_view_id = parse_feishu_url(url)
        wiki_token = parsed_app_token
        app_token = app_token or parsed_app_token
        table_id = table_id or parsed_table_id
        view_id = view_id or parsed_view_id
    
    if not app_token:
        print("❌ 缺少 app_token")
        return None
    
    print(f"📊 Wiki Token: {wiki_token}")
    print(f"📋 Table ID: {table_id or '(将列出所有表)'}")
    print(f"👁️ View ID: {view_id or '(默认视图)'}")
    print()
    
    # 尝试从知识库节点获取真正的 bitable token
    if wiki_token:
        real_app_token = get_bitable_token_from_wiki(token, wiki_token)
        if real_app_token and real_app_token != wiki_token:
            print(f"📊 Bitable App Token: {real_app_token}")
            app_token = real_app_token
    
    print()
    
    # 如果没有指定 table_id，列出所有表
    if not table_id:
        tables = list_tables(token, app_token)
        if tables:
            print("📑 可用的表格：")
            for t in tables:
                print(f"  - {t.get('name')} (ID: {t.get('table_id')})")
            # 使用第一个表
            table_id = tables[0].get("table_id")
            print(f"\n使用第一个表格: {tables[0].get('name')}")
        else:
            print("❌ 未找到任何表格")
            return None
    
    # 获取字段定义
    fields = get_table_fields(token, app_token, table_id)
    field_map = {f["field_id"]: f for f in fields}
    field_names = [f["field_name"] for f in fields]
    
    print(f"📝 字段: {', '.join(field_names)}")
    print()
    
    # 获取记录
    records = get_table_records(token, app_token, table_id, view_id)
    print(f"📊 共 {len(records)} 条记录")
    print("=" * 60)
    
    # 检查是否有非空记录
    non_empty_records = [r for r in records if r.get("fields")]
    if not non_empty_records and records:
        print("\n⚠️ 所有记录都是空行（没有填写数据）")
    
    # 输出记录
    for i, record in enumerate(records, 1):
        record_fields = record.get("fields", {})
        if not record_fields:
            continue  # 跳过空记录
        
        print(f"\n【记录 {i}】")
        for field in fields:
            field_name = field["field_name"]
            field_id = field["field_id"]
            field_type = field["type"]
            # 尝试用 field_name 或 field_id 获取值
            value = record_fields.get(field_name) or record_fields.get(field_id)
            formatted_value = format_field_value(value, field_type)
            if formatted_value:
                print(f"  {field_name}: {formatted_value}")
    
    return {
        "fields": fields,
        "records": records,
        "field_names": field_names
    }


def main():
    parser = argparse.ArgumentParser(description="读取飞书多维表格")
    parser.add_argument("--url", "-u", help="飞书多维表格 URL")
    parser.add_argument("--app-token", "-a", help="Bitable App Token")
    parser.add_argument("--table-id", "-t", help="Table ID")
    parser.add_argument("--view-id", "-v", help="View ID")
    
    args = parser.parse_args()
    
    if not args.url and not args.app_token:
        print("用法:")
        print('  python read_bitable.py --url "https://my.feishu.cn/wiki/xxx?table=xxx"')
        print("  python read_bitable.py --app-token xxx --table-id xxx")
        return
    
    read_bitable(
        url=args.url,
        app_token=args.app_token,
        table_id=args.table_id,
        view_id=args.view_id
    )


if __name__ == "__main__":
    main()
