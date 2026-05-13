import re
from typing import Optional, Tuple

SALARY_BINS = [
    ('<5K', 0, 5000),
    ('5K-10K', 5000, 10000),
    ('10K-20K', 10000, 20000),
    ('20K-35K', 20000, 35000),
    ('35K+', 35000, 999999),
    ('面议', None, None),
]

SALARY_BIN_LABELS = [b[0] for b in SALARY_BINS]


def parse_salary(salary_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    解析薪资格式，返回 (月薪下限, 月薪上限)
    支持: '15k-25k', '15000-25000元/月', '20-30万/年', '3K-5K·15薪', '200-300元/天'
    """
    if not salary_text or '面议' in salary_text:
        return None, None

    text = salary_text.strip().lower().replace(',', '').replace('，', '')

    # 日薪模式: 200-300元/天
    if '天' in text or '日' in text:
        return _extract_range(text)

    # 年薪模式: 20-30万/年
    is_annual = '年' in text
    nums = _extract_range(text)

    if is_annual and nums[0] is not None:
        nums = (nums[0] / 12, nums[1] / 12 if nums[1] else None)

    return nums


def _extract_range(text: str) -> Tuple[Optional[float], Optional[float]]:
    """提取数字范围"""
    # 清理干扰字符: 15薪、13薪等
    text = re.sub(r'\d+\s*薪', '', text)

    # 扩展范围末尾的单位到两边: "20-30万" -> "20万-30万"
    text = re.sub(
        r'(\d+(?:\.\d+)?)\s*[-~到至]\s*(\d+(?:\.\d+)?)\s*([kK万千])\b',
        lambda m: f'{m.group(1)}{m.group(3)}-{m.group(2)}{m.group(3)}',
        text
    )

    # 处理单位：K、万、千
    text = re.sub(r'(\d+(?:\.\d+)?)\s*[kK]', lambda m: str(float(m.group(1)) * 1000), text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*万', lambda m: str(float(m.group(1)) * 10000), text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s*千', lambda m: str(float(m.group(1)) * 1000), text)

    # 匹配数字-数字模式
    match = re.search(r'([\d.]+)\s*[-~到至]\s*([\d.]+)', text)
    if match:
        return float(match.group(1)), float(match.group(2))

    # 匹配单个数字
    match = re.search(r'([\d.]+)', text)
    if match:
        val = float(match.group(1))
        return val, val

    return None, None


def classify_salary_range(salary_min: Optional[float], salary_max: Optional[float]) -> str:
    """将薪资数字归入档位"""
    if salary_min is None:
        return '面议'

    mid = (salary_min + (salary_max or salary_min)) / 2

    for label, lo, hi in SALARY_BINS:
        if lo is None:
            continue
        if lo <= mid < hi:
            return label

    return '35K+'
