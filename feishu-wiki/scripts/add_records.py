#!/usr/bin/env python3
"""
添加职位记录到飞书多维表格
"""

import requests
import json
import argparse
from pathlib import Path

APP_ID = "cli_a9f6d47ef9fa5cd5"
APP_SECRET = "REMOVED_FEISHU_SECRET"
BASE_URL = "https://open.feishu.cn/open-apis"

BITABLE_APP_TOKEN = "BUkFb4Izna2q0Ys2BOXc8i6Hnsf"
TABLE_ID = "tbl8sCnDARGYuu8W"

# 字段名称映射
FIELD_NAMES = {
    "文本": "文本",
    "公司": "公司",
    "职务": "职务",
    "类别": "类别",
    "薪资": "薪资",
    "特殊要求": "特殊要求",
}


def get_token():
    """获取 tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    raise Exception(f"获取 token 失败: {result}")


def get_fields(token: str) -> dict:
    """获取字段 ID 映射"""
    url = f"{BASE_URL}/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    result = response.json()

    if result.get("code") == 0:
        fields = result.get("data", {}).get("items", [])
        return {f["field_name"]: f["field_id"] for f in fields}
    raise Exception(f"获取字段失败: {result}")


def add_records(token: str, records: list) -> dict:
    """添加记录到多维表格"""
    url = f"{BASE_URL}/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {"records": records}

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if result.get("code") == 0:
        return result.get("data", {})
    raise Exception(f"添加记录失败: {result}")


def prepare_records(jobs_data: list) -> list:
    """准备记录数据"""
    records = []

    for job in jobs_data:
        fields = {}

        # 文本 - 包含申请链接
        text_field = FIELD_NAMES.get("文本")
        if text_field and job.get("apply_url"):
            fields[text_field] = (
                f"{job['description'][:500]}\n\n申请链接: {job['apply_url']}"
            )

        # 公司
        company_field = FIELD_NAMES.get("公司")
        if company_field:
            fields[company_field] = job.get("company", "")

        # 职务 - 职位标题
        title_field = FIELD_NAMES.get("职务")
        if title_field:
            fields[title_field] = job.get("title", "")

        # 类别 - 职位类型
        category_field = FIELD_NAMES.get("类别")
        if category_field:
            fields[category_field] = job.get("position_type", "")

        # 薪资
        salary_field = FIELD_NAMES.get("薪资")
        if salary_field:
            fields[salary_field] = job.get("salary", "")

        # 特殊要求 - 标签
        tags_field = FIELD_NAMES.get("特殊要求")
        if tags_field and job.get("tags"):
            tags_text = ", ".join(job.get("tags", []))
            fields[tags_field] = tags_text

        if fields:
            records.append({"fields": fields})

    return records


def load_jobs_from_json(json_path: str) -> list:
    """从 JSON 文件加载职位数据"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="添加职位到飞书多维表格")
    parser.add_argument("--file", "-f", help="职位数据 JSON 文件路径")
    parser.add_argument("--data", "-d", help="JSON 格式的职位数据")

    args = parser.parse_args()

    # 获取 token
    print("🔐 获取飞书访问令牌...")
    token = get_token()

    # 加载数据
    if args.file:
        print(f"📂 从文件加载: {args.file}")
        jobs = load_jobs_from_json(args.file)
    elif args.data:
        print("📥 解析传入的数据...")
        jobs = json.loads(args.data)
    else:
        print("❌ 请提供 --file 或 --data 参数")
        return

    print(f"📊 准备添加 {len(jobs)} 条记录...")

    # 准备记录
    records = prepare_records(jobs)
    print(f"✅ 准备完成 {len(records)} 条有效记录")

    # 添加记录
    if records:
        print("🚀 正在添加到飞书多维表格...")
        result = add_records(token, records)
        print(f"✅ 成功添加 {len(records)} 条记录!")
        print(
            f"📋 多维表格: https://my.feishu.cn/base/{BITABLE_APP_TOKEN}?table={TABLE_ID}"
        )
    else:
        print("⚠️ 没有有效数据可添加")


if __name__ == "__main__":
    main()
