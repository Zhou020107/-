from abc import ABC, abstractmethod
from typing import Generator
from datetime import datetime
from utils.helpers import random_delay


class BaseScraper(ABC):
    """爬虫基类 — 所有网站爬虫继承此类"""

    site_name: str = ""
    base_url: str = ""
    encoding: str = "utf-8"
    use_browser: bool = False

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.min_delay = self.config.get('min_delay_seconds', 3)
        self.max_delay = self.config.get('max_delay_seconds', 8)

    @abstractmethod
    def search(self, keyword: str, location: str = "", max_pages: int = 5) -> Generator[dict, None, None]:
        """搜索职位，逐条返回结果"""
        ...

    def parse_page(self, html_or_response) -> list[dict]:
        """解析一页的职位数据（默认空实现，JSON API 类爬虫不需要）"""
        return []

    def normalize_item(self, raw: dict) -> dict:
        """将网站特有字段映射为标准字段"""
        return {
            'url': raw.get('url', ''),
            'title': raw.get('title', ''),
            'company': raw.get('company', ''),
            'location': raw.get('location', ''),
            'salary_text': raw.get('salary_text', ''),
            'salary_min': raw.get('salary_min'),
            'salary_max': raw.get('salary_max'),
            'education': raw.get('education', ''),
            'experience': raw.get('experience', ''),
            'description': raw.get('description', ''),
            'source': raw.get('source', self.site_name),
            'post_date': raw.get('post_date', ''),
            'job_type': raw.get('job_type', ''),
            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def delay(self):
        """请求间随机延迟"""
        random_delay(self.min_delay, self.max_delay)
