"""Markdown 格式生成器"""

from datetime import datetime
from typing import Any


class MarkdownFormatter:
    """Markdown 文档生成器"""

    def __init__(self, category: str = "Development"):
        self.category = category

    def format(self, jobs: list[dict]) -> str:
        """生成 Markdown 文档"""
        lines = [
            self._generate_header(jobs),
            self._generate_stats(jobs),
            self._generate_job_list(jobs),
        ]
        return "\n".join(lines)

    def _generate_header(self, jobs: list[dict]) -> str:
        """生成文档头部"""
        return f"""# Working Nomads {self.category} 职位列表

> 更新日期: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> 职位数量: {len(jobs)}
> 数据来源: Working Nomads (https://www.workingnomads.com/jobs)

---

"""

    def _generate_stats(self, jobs: list[dict]) -> str:
        """生成统计信息"""
        full_time = sum(1 for j in jobs if j["position_type"] == "Full-time")
        part_time = sum(1 for j in jobs if j["position_type"] == "Part-time")
        freelance = sum(1 for j in jobs if j["position_type"] == "Freelance")
        with_salary = sum(1 for j in jobs if j["salary"] != "Not specified")

        return f"""## 📊 统计概览

| 指标 | 数量 |
|------|------|
| 全职职位 | {full_time} |
| 兼职职位 | {part_time} |
| 自由职业 | {freelance} |
| 有薪资信息 | {with_salary} |

---

"""

    def _generate_job_list(self, jobs: list[dict]) -> str:
        """生成职位列表"""
        lines = ["## 💼 职位列表\n"]

        for idx, job in enumerate(jobs, 1):
            lines.extend(
                [
                    f"### {idx}. {job['title']}",
                    "",
                    f"**🏢 公司:** {job['company']}",
                    f"**📍 地点:** {job['location']}",
                    f"**💼 类型:** {job['position_type']}",
                    f"**💰 薪资:** {job['salary']}",
                    f"**📊 经验:** {job['experience']}",
                    f"**🏷️ 标签:** {', '.join(job['tags']) if job['tags'] else 'N/A'}",
                    "",
                    f"**📝 描述:**",
                    "",
                    f">{self._truncate_description(job['description'])}",
                    "",
                ]
            )

            if job["apply_url"]:
                lines.append(f"**🔗 [申请职位]({job['apply_url']})**")

            lines.append("\n---\n")

        return "\n".join(lines)

    def _truncate_description(self, description: str, max_length: int = 200) -> str:
        """截断描述文本"""
        if len(description) <= max_length:
            return description
        return description[:max_length].strip() + "..."


def generate_markdown(jobs: list[dict], category: str = "Development") -> str:
    """生成 Markdown 文档"""
    formatter = MarkdownFormatter(category)
    return formatter.format(jobs)
