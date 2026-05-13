import re

# 技术栈关键词词典（框架/工具 -> 归属类别）
TECH_KEYWORDS = {
    'Python': ['python', 'django', 'flask', 'fastapi', 'tornado', 'scrapy', 'selenium'],
    'Java': ['java', 'spring', 'mybatis', 'hibernate', 'jvm', 'jdk'],
    'JavaScript/TS': ['javascript', 'js', 'typescript', 'ts', 'node'],
    '前端': ['react', 'vue', 'angular', 'html', 'css', 'jquery', 'bootstrap',
            '小程序', 'webpack', 'vite', 'next', 'nuxt', 'uniapp'],
    '后端': ['golang', 'go', 'rust', 'c\\+\\+', 'c#', 'php', 'ruby', 'nginx',
            '微服务', '分布式', 'rpc', 'grpc'],
    '数据': ['sql', 'mysql', 'mongodb', 'redis', 'postgresql', 'oracle',
            'hadoop', 'spark', 'flink', 'kafka', 'elasticsearch', 'etl'],
    'AI/算法': ['机器学习', '深度学习', 'nlp', '计算机视觉', 'cv', '大模型',
              'tensorflow', 'pytorch', 'transformer', 'llm', 'aigc'],
    '移动端': ['android', 'ios', 'flutter', 'react native', 'kotlin', 'swift',
             'objective-c', '鸿蒙'],
    '运维/DevOps': ['docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab',
                  'devops', 'cicd', 'terraform', 'linux'],
    '数据分析': ['excel', 'tableau', 'power bi', '数据分析', '数据挖掘',
               '可视化'],
    '测试': ['自动化测试', '性能测试', 'selenium', 'appium', 'jmeter'],
}


def detect_tech_stack(title: str, description: str = "") -> list[str]:
    """从标题和描述中检测技术栈"""
    text = (title + ' ' + description).lower()
    found = []

    for category, keywords in TECH_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                found.append(category)
                break

    return found


# 福利待遇关键词
INSURANCE_KEYWORDS = ['五险一金', '六险一金', '五险', '六险', '社保', '公积金',
                       '七险一金', '五险二金', '补充医疗保险', '商业保险']

WEEKEND_OFF_KEYWORDS = ['双休', '周末双休', '周末休息', '双休制', '周休二日',
                         '做五休二', '不加班', '五天工作制', '工作日5天']

GRADUATE_KEYWORDS = ['应届生', '应届', '应届毕业生', '毕业生', '校招', '校园招聘',
                      '可接受应届', '接受应届', '欢迎应届', '面向应届',
                      '实习转正', '可转正', '管培生', '培训生', '接受无经验',
                      '不限经验', '无经验要求', '经验不限']


def detect_welfare(description: str, tags: str = "") -> dict:
    """
    从描述和标签中检测福利待遇
    返回 {is_accept_graduate, has_weekend_off, has_insurance}
    """
    text = (description + ' ' + tags).lower()

    has_insurance = any(kw.lower() in text for kw in INSURANCE_KEYWORDS)
    has_weekend_off = any(kw.lower() in text for kw in WEEKEND_OFF_KEYWORDS)
    is_accept_graduate = any(kw.lower() in text for kw in GRADUATE_KEYWORDS)

    return {
        'is_accept_graduate': is_accept_graduate,
        'has_weekend_off': has_weekend_off,
        'has_insurance': has_insurance,
    }
