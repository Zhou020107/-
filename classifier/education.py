import re

EDUCATION_PATTERNS = [
    (r'博士', '博士'),
    (r'硕士|研究生', '硕士'),
    (r'本科|学士|全日制大学', '本科'),
    (r'大专|专科', '大专'),
    (r'中专|高中|中技', '高中/中专'),
    (r'学历不限|无学历要求|不限学历', '不限'),
]

EDUCATION_ORDER = ['博士', '硕士', '本科', '大专', '高中/中专', '不限']


def classify_education(title: str, description: str = "", raw_education: str = "") -> str:
    """从文本中识别学历要求"""
    text = f"{title} {description} {raw_education}".lower()

    for pattern, label in EDUCATION_PATTERNS:
        if re.search(pattern, text):
            return label

    return '未知'
