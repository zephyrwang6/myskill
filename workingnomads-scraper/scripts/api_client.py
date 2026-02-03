"""Working Nomads API 客户端"""

import requests


class WorkingNomadsAPI:
    """Working Nomads Elasticsearch API 客户端"""

    BASE_URL = "https://www.workingnomads.com/jobsapi/_search"

    POSITION_TYPES = {"ft": "Full-time", "fr": "Freelance", "pt": "Part-time"}

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "WorkingNomads-Scraper/1.0",
            }
        )

    def fetch_jobs(
        self,
        category: str = "Development",
        size: int = 50,
        salary_min: int = None,
        salary_max: int = None,
    ) -> list[dict]:
        """
        从 Working Nomads API 获取职位数据
        """
        query = self._build_query(category, salary_min, salary_max)

        payload = {
            "track_total_hits": True,
            "from": 0,
            "size": size,
            "_source": [
                "id",
                "title",
                "company",
                "category_name",
                "description",
                "position_type",
                "salary_range",
                "annual_salary_usd",
                "tags",
                "locations",
                "apply_url",
                "pub_date",
                "experience_level",
            ],
            "query": query,
        }

        response = self.session.post(self.BASE_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["hits"]["hits"]

    def _build_query(self, category: str, salary_min: int, salary_max: int) -> dict:
        """构建 Elasticsearch 查询"""
        filters = []

        if category == "Development":
            filters.append(
                {
                    "terms": {
                        "category_name.raw": [
                            "Development",
                            "Design",
                            "Web Development",
                        ]
                    }
                }
            )
        else:
            filters.append({"terms": {"category_name.raw": [category]}})

        if salary_min or salary_max:
            salary_filter = {"range": {"annual_salary_usd": {}}}
            if salary_min:
                salary_filter["range"]["annual_salary_usd"]["gte"] = salary_min
            if salary_max:
                salary_filter["range"]["annual_salary_usd"]["lte"] = salary_max
            filters.append(salary_filter)

        return {"bool": {"filter": filters}}
