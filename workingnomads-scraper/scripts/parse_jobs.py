#!/usr/bin/env python3
"""
解析 Markdown 文件，提取职位数据为 JSON
"""

import re
import json
from pathlib import Path


def parse_markdown_jobs(markdown_path: str) -> list:
    """从 Markdown 文件解析职位数据"""

    content = Path(markdown_path).read_text(encoding="utf-8")

    jobs = []
    current_job = None

    lines = content.split("\n")

    for line in lines:
        # 检测新职位开始
        title_match = re.match(r"^### \d+\. (.+)$", line)
        if title_match:
            if current_job:
                jobs.append(current_job)
            current_job = {
                "title": title_match.group(1),
                "company": "",
                "location": "",
                "position_type": "",
                "salary": "",
                "experience": "",
                "tags": [],
                "description": "",
                "apply_url": "",
            }
            continue

        if current_job:
            # 公司
            if line.startswith("**🏢 公司:**"):
                current_job["company"] = line.replace("**🏢 公司:**", "").strip()

            # 地点
            elif line.startswith("**📍 地点:**"):
                current_job["location"] = line.replace("**📍 地点:**", "").strip()

            # 类型
            elif line.startswith("**💼 类型:**"):
                current_job["position_type"] = line.replace("**💼 类型:**", "").strip()

            # 薪资
            elif line.startswith("**💰 薪资:**"):
                current_job["salary"] = line.replace("**💰 薪资:**", "").strip()

            # 经验
            elif line.startswith("**📊 经验:**"):
                current_job["experience"] = line.replace("**📊 经验:**", "").strip()

            # 标签
            elif line.startswith("**🏷️ 标签:**"):
                tags_str = line.replace("**🏷️ 标签:**", "").strip()
                current_job["tags"] = [
                    t.strip() for t in tags_str.split(",") if t.strip()
                ]

            # 描述
            elif line.startswith(">"):
                desc_line = line.strip().replace(">", "").strip()
                if desc_line:
                    current_job["description"] = desc_line

            # 申请链接
            elif line.startswith("**🔗 [申请职位]"):
                url_match = re.search(r"\((.+)\)", line)
                if url_match:
                    current_job["apply_url"] = url_match.group(1)

    # 添加最后一个职位
    if current_job:
        jobs.append(current_job)

    return jobs


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python parse_jobs.py <markdown_file>")
        return

    md_path = sys.argv[1]
    jobs = parse_markdown_jobs(md_path)

    print(f"📊 解析到 {len(jobs)} 个职位")

    # 输出 JSON
    output_path = md_path.replace(".md", ".json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存到: {output_path}")

    # 返回 JSON 数据（用于传递给 add_records.py）
    print("\n" + "=" * 60)
    print(json.dumps(jobs, ensure_ascii=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
