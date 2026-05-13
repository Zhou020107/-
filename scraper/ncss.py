import httpx
from typing import Generator
from datetime import datetime
from utils.helpers import clean_text, random_delay
from utils.logger import setup_logger
from .base import BaseScraper

logger = setup_logger()

NCSS_API = "https://24365.smartedu.cn/student/jobs/jobslist/ajax/"

# 招聘类型映射
JOB_TYPE_MAP = {"01": "全职", "02": "兼职", "03": "实习"}


class NCSSScraper(BaseScraper):
    """国家大学生就业服务平台爬虫 — 基于 JSON API"""

    site_name = "国家大学生就业服务平台"
    base_url = "https://24365.smartedu.cn"
    encoding = "utf-8"
    use_browser = False

    def search(self, keyword: str, location: str = "", max_pages: int = 5) -> Generator[dict, None, None]:
        """搜索职位"""
        offset = 1
        limit = 20
        page = 0

        while page < max_pages:
            params = {
                'jobType': '',
                'areaCode': '',
                'jobName': keyword,
                'monthPay': '',
                'industrySectors': '',
                'property': '',
                'categoryCode': '',
                'memberLevel': '',
                'recruitType': '',
                'offset': offset,
                'limit': limit,
                'keyUnits': '',
                'degreeCode': '',
                'sourcesName': '0',
                'sourcesType': '',
            }

            logger.info(f"NCSS: 第{page + 1}页, offset={offset}")

            try:
                resp = httpx.get(
                    NCSS_API,
                    params=params,
                    headers=self._headers(),
                    timeout=30,
                )
                data = resp.json()

                if not data.get('flag'):
                    logger.warning(f"NCSS: API返回失败")
                    break

                job_list = data.get('data', {}).get('list', [])
                if not job_list:
                    logger.info(f"NCSS: 第{page + 1}页无结果")
                    break

                for job in job_list:
                    item = self._parse_item(job)
                    if item and item.get('title'):
                        yield item

                pagination = data.get('data', {}).get('pagenation', {})
                total = pagination.get('total', 0)
                if offset >= total:
                    break

                page += 1
                offset += limit

                if page < max_pages:
                    random_delay(self.min_delay, self.max_delay)

            except Exception as e:
                logger.error(f"NCSS 第{page + 1}页失败: {e}")
                break

    def _parse_item(self, job: dict) -> dict:
        """解析单条职位数据"""
        title = clean_text(job.get('jobName', ''))

        # 薪资
        low_pay = job.get('lowMonthPay') or 0
        high_pay = job.get('highMonthPay') or 0
        if low_pay and high_pay:
            salary_text = f"{low_pay:.0f}K-{high_pay:.0f}K"
        elif high_pay:
            salary_text = f"{high_pay:.0f}K"
        elif low_pay:
            salary_text = f"{low_pay:.0f}K"
        else:
            salary_text = '面议'

        # 福利标签
        rec_tags = clean_text(job.get('recTags', ''))  # 五险一金, 年终奖, 住房补助等

        # 发布日期
        publish_ts = job.get('publishDate')
        if publish_ts:
            try:
                publish_date = datetime.fromtimestamp(publish_ts / 1000).strftime('%Y-%m-%d')
            except (ValueError, OSError):
                publish_date = ''
        else:
            publish_date = ''

        # 学历
        degree = clean_text(job.get('degreeName', ''))  # 本科及以上, 硕士及以上

        return {
            'url': f"https://24365.smartedu.cn/student/jobs/{job.get('jobId', '')}",
            'title': title,
            'company': clean_text(job.get('recName', '')),
            'location': clean_text(job.get('areaCodeName', '')),
            'salary_text': salary_text,
            'salary_min': float(low_pay) * 1000 if low_pay else None,
            'salary_max': float(high_pay) * 1000 if high_pay else None,
            'education': degree,
            'experience': '',
            'description': clean_text(job.get('major', '')),
            'source': '国家大学生就业服务平台',
            'post_date': publish_date,
            'job_type': '全职',
            'rec_tags': rec_tags,  # 福利标签（用于分类）
            'is_accept_graduate': True,  # 该平台专为大学生服务
            'head_count': job.get('headCount', 0),
            'company_scale': clean_text(job.get('recScale', '')),
            'company_property': clean_text(job.get('recProperty', '')),
        }

    def _headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://24365.smartedu.cn/student/jobs/index.html',
        }
