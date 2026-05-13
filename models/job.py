from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class JobItem:
    """标准化的职位数据模型"""
    url: str                              # 详情链接（用于去重）
    title: str                            # 职位名称
    company: str = ""                     # 公司名称
    location: str = ""                    # 工作地点（原始文本）
    location_tier: str = ""               # 城市等级（分类后填充）
    salary_text: str = ""                 # 薪资原文
    salary_min: Optional[float] = None    # 月薪下限
    salary_max: Optional[float] = None    # 月薪上限
    salary_range: str = ""                # 薪资档位（分类后填充）
    education: str = ""                   # 学历要求（分类后填充）
    experience: str = ""                  # 经验要求
    tech_stack: list = field(default_factory=list)  # 技术栈标签
    description: str = ""                 # 职位描述
    source: str = ""                      # 来源网站
    post_date: str = ""                   # 发布日期
    job_type: str = ""                    # 全职/实习/兼职
    is_accept_graduate: bool = False      # 是否接受应届生
    has_weekend_off: bool = False         # 是否双休
    has_insurance: bool = False           # 是否有五险一金
    scraped_at: str = ""                  # 爬取时间

    def to_dict(self) -> dict:
        d = asdict(self)
        d['tech_stack'] = ','.join(self.tech_stack) if self.tech_stack else ''
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'JobItem':
        tech = d.get('tech_stack', '')
        if isinstance(tech, str):
            tech = [t.strip() for t in tech.split(',') if t.strip()]
        d['tech_stack'] = tech
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
