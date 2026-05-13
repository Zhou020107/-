import json
import re
from typing import Generator
from utils.helpers import clean_text, random_delay
from utils.logger import setup_logger
from .base import BaseScraper

logger = setup_logger()

CITY_CODES = {
    "北京": "010000", "上海": "020000", "广州": "030200", "深圳": "040000",
    "杭州": "080200", "成都": "090200", "武汉": "180200", "南京": "070200",
    "": "000000",
}


class Job51Scraper(BaseScraper):
    """51job 爬虫 — 基于 Playwright 浏览器"""

    site_name = "51job"
    base_url = "https://we.51job.com"
    encoding = "utf-8"
    use_browser = True

    def search(self, keyword: str, location: str = "", max_pages: int = 5) -> Generator[dict, None, None]:
        city_code = CITY_CODES.get(location, "000000")

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
            )
            page = context.new_page()

            for page_num in range(1, max_pages + 1):
                url = (
                    f"https://we.51job.com/pc/search"
                    f"?keyword={keyword}&searchType=2&jobArea={city_code}"
                    f"&pageNum={page_num}&pageSize=20"
                )
                logger.info(f"51job: 第{page_num}页")

                try:
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    page.wait_for_timeout(3000)

                    # 检查是否有反爬验证
                    content = page.content()
                    if '请输入验证码' in content or 'arg1' in content[:500]:
                        logger.warning("51job: 触发反爬验证")
                        break

                    items = self.parse_page(page)
                    if not items:
                        logger.info(f"51job: 第{page_num}页无结果")
                        break

                    for item in items:
                        yield item

                    if page_num < max_pages:
                        random_delay(self.min_delay, self.max_delay)

                except Exception as e:
                    logger.error(f"51job 第{page_num}页失败: {e}")
                    break

            browser.close()

    def parse_page(self, page) -> list[dict]:
        """解析搜索结果页（Playwright page 对象）"""
        items = []

        cards = page.query_selector_all('.joblist-item')
        if not cards:
            return items

        for card in cards:
            try:
                item = self._parse_card(card)
                if item and item.get('title'):
                    items.append(item)
            except Exception as e:
                logger.error(f"解析51job卡片失败: {e}")

        return items

    def _parse_card(self, card) -> dict:
        """解析单个职位卡片"""
        # 优先从 sensorsdata 属性提取结构化数据
        wrapper = card.query_selector('.joblist-item-job')
        sensors_data = {}

        if wrapper:
            attr = wrapper.get_attribute('sensorsdata')
            if attr:
                try:
                    sensors_data = json.loads(attr)
                except json.JSONDecodeError:
                    pass

        # 从 sensorsdata 提取
        title = sensors_data.get('jobTitle', '')
        salary_text = sensors_data.get('jobSalary', '')
        raw_education = sensors_data.get('jobDegree', '')
        post_date = sensors_data.get('jobTime', '')

        # 从 DOM 提取（作为补充和验证）
        # 职位名
        if not title:
            title_el = card.query_selector('.jname')
            if title_el:
                title = clean_text(title_el.get_attribute('title') or title_el.inner_text())

        # 薪资
        if not salary_text:
            sal_el = card.query_selector('.sal')
            if sal_el:
                salary_text = clean_text(sal_el.inner_text())

        # 公司
        company = ''
        comp_el = card.query_selector('.comp')
        if comp_el:
            comp_name_el = comp_el.query_selector('.bl')
            if not comp_name_el:
                comp_name_el = comp_el
            company = clean_text(comp_name_el.inner_text()) if comp_name_el else ''

        # 地点
        location = sensors_data.get('jobArea', '')
        if not location:
            area_el = card.query_selector('.area .shrink-0')
            if area_el:
                location = clean_text(area_el.inner_text())

        # 经验要求
        experience = sensors_data.get('jobYear', '')

        # 职位描述/标签
        description = ''
        tag_els = card.query_selector_all('.tag')
        tags = [clean_text(t.inner_text()) for t in tag_els if t.inner_text()]
        if tags:
            description = ', '.join(tags)

        # 获取详情链接
        url = ''
        link_el = card.query_selector('a[href*="jobs.51job.com"]')
        if link_el:
            url = link_el.get_attribute('href') or ''

        return {
            'url': url,
            'title': title,
            'company': company,
            'location': location,
            'salary_text': salary_text,
            'education': clean_text(raw_education),
            'experience': clean_text(experience),
            'description': description,
            'source': '51job',
            'post_date': post_date,
            'job_type': '全职',
        }
