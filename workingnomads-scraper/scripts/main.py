#!/usr/bin/env python3
"""
Working Nomads Scraper - 主入口脚本
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

from .api_client import WorkingNomadsAPI
from .parser import parse_jobs
from .markdown_formatter import generate_markdown


def main():
    parser = argparse.ArgumentParser(description="从 Working Nomads 抓取职位数据")
    parser.add_argument(
        "--category",
        "-c",
        default="Development",
        help="职位类别 (default: Development)",
    )
    parser.add_argument(
        "--size", "-s", type=int, default=50, help="抓取数量 (default: 50)"
    )
    parser.add_argument(
        "--output-dir", "-o", default="data", help="输出目录 (default: data)"
    )

    args = parser.parse_args()

    print(f"📡 正在从 Working Nomads API 抓取 {args.category} 职位...")
    api = WorkingNomadsAPI()
    raw_jobs = api.fetch_jobs(category=args.category, size=args.size)
    print(f"✅ 获取到 {len(raw_jobs)} 条原始数据")

    print("🔧 正在解析数据...")
    jobs = parse_jobs(raw_jobs)
    print(f"✅ 解析完成")

    print("📝 正在生成 Markdown...")
    markdown = generate_markdown(jobs, category=args.category)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{args.category.lower()}_jobs_{timestamp}.md"
    filepath = output_dir / filename

    filepath.write_text(markdown, encoding="utf-8")
    print(f"✅ Markdown 已保存到: {filepath}")

    with_salary = sum(1 for j in jobs if j["salary"] != "Not specified")
    print(f"\n📊 统计:")
    print(f"   - 总职位数: {len(jobs)}")
    print(f"   - 有薪资信息: {with_salary}")

    return str(filepath)


if __name__ == "__main__":
    main()
