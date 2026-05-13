import yaml
import os
from typing import Generator, Callable
from utils.logger import setup_logger
from .base import BaseScraper

logger = setup_logger()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')


def load_config() -> dict:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class ScraperManager:
    """爬虫管理器 — 协调所有网站爬虫"""

    def __init__(self, config: dict = None):
        self.config = config or load_config()
        self.scrapers: list[BaseScraper] = []
        self._init_scrapers()

    def _init_scrapers(self):
        """根据配置初始化启用的爬虫"""
        sites_config = self.config.get('sites', {})
        scraping_config = self.config.get('scraping', {})

        if sites_config.get('51job', {}).get('enabled', True):
            from .job51 import Job51Scraper
            self.scrapers.append(Job51Scraper(scraping_config))

        if sites_config.get('ncss', {}).get('enabled', True):
            from .ncss import NCSSScraper
            self.scrapers.append(NCSSScraper(scraping_config))

        if sites_config.get('shixiseng', {}).get('enabled', False):
            pass

    def get_enabled_sites(self) -> list[str]:
        """返回启用的网站名称列表"""
        return [s.site_name for s in self.scrapers]

    def search_all(
        self,
        keyword: str,
        location: str = "",
        max_pages: int = 5,
        progress_callback: Callable = None,
    ) -> Generator[dict, None, None]:
        """在所有启用的网站上搜索"""
        for scraper in self.scrapers:
            site = scraper.site_name
            logger.info(f"开始爬取 {site}, 关键词={keyword}, 地点={location}")

            if progress_callback:
                progress_callback(site, 'running', f"正在爬取 {site}...")

            count = 0
            try:
                for item in scraper.search(keyword, location, max_pages):
                    # 分类器会在调用方处理
                    yield item
                    count += 1

                if progress_callback:
                    progress_callback(site, 'success', f"{site}: 完成，获取 {count} 条")

            except Exception as e:
                logger.error(f"{site} 爬取失败: {e}")
                if progress_callback:
                    progress_callback(site, 'failed', f"{site}: 失败 - {str(e)[:80]}")
