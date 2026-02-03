"""数据解析和清洗模块"""

import re
from datetime import datetime
from typing import Any


class JobParser:
    """职位数据解析器"""

    POSITION_TYPES = {"ft": "Full-time", "fr": "Freelance", "pt": "Part-time"}

    EXPERIENCE_MAP = {
        "ENTRY_LEVEL": "Entry Level",
        "MID_LEVEL": "Mid Level",
        "SENIOR_LEVEL": "Senior Level",
        "EXECUTIVE": "Executive",
    }

    def parse(self, raw_job: dict) -> dict:
        """解析单条职位数据"""
        source = raw_job["_source"]

        return {
            "id": source.get("id"),
            "title": source.get("title", "N/A"),
            "company": source.get("company", "N/A"),
            "category": source.get("category_name", "N/A"),
            "location": self._format_location(source.get("locations")),
            "position_type": self.POSITION_TYPES.get(
                source.get("position_type", "ft"), "Full-time"
            ),
            "salary": self._format_salary(source),
            "experience": self.EXPERIENCE_MAP.get(
                source.get("experience_level", ""), "Not specified"
            ),
            "tags": source.get("tags", []) or [],
            "description": self._clean_html(source.get("description", "")),
            "apply_url": source.get("apply_url", ""),
            "pub_date": self._format_date(source.get("pub_date")),
        }

    def _format_location(self, locations: list) -> str:
        """格式化地点"""
        if not locations:
            return "Remote"
        return ", ".join(locations[:3])

    def _format_salary(self, source: dict) -> str:
        """格式化薪资信息"""
        annual = source.get("annual_salary_usd")
        range_str = source.get("salary_range_short") or source.get("salary_range")

        if annual:
            return f"${annual:,}/year"
        elif range_str:
            return range_str
        return "Not specified"

    def _clean_html(self, html: str) -> str:
        """清理 HTML 标签"""
        if not html:
            return ""

        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return date_str


def parse_jobs(raw_jobs: list[dict]) -> list[dict]:
    """批量解析职位数据"""
    parser = JobParser()
    return [parser.parse(job) for job in raw_jobs]
