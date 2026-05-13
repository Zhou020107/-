import re
import random
import time
from functools import wraps


def random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """随机延迟，模拟人类浏览行为"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def retry_on_failure(max_retries: int = 3, delay: float = 5.0):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def clean_text(text: str) -> str:
    """清理文本：去除多余空白和特殊字符"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def extract_number(text: str) -> float:
    """从文本中提取第一个数字"""
    if not text:
        return 0
    match = re.search(r'[\d.]+', str(text))
    return float(match.group()) if match else 0
