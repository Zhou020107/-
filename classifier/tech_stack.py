import re
import os

# ── 技术栈关键词词典（领域 → 关键词列表）──
TECH_KEYWORDS = {
    # 计算机/IT
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
    '数据分析': ['excel', 'tableau', 'power bi', '数据分析', '数据挖掘', '可视化'],
    '测试': ['自动化测试', '性能测试', 'selenium', 'appium', 'jmeter'],

    # 金融/会计/财务
    '财务会计': ['会计', '财务', '审计', '税务', '用友', '金蝶', 'sap', 'oracle财务',
               'cpa', 'acca', '中级会计', '初级会计', '注册会计师', '报税', '记账',
               '财务分析', '成本核算', '出纳', '对账', '发票管理', '用友u8', 'nc'],
    '金融分析': ['bloomberg', 'wind', 'cfa', 'frm', '量化交易', '风控', '投行',
               '行研', '行业研究', '基金管理', '证券', '期货', '保险', '信贷'],

    # 建筑/工程/施工
    '建筑设计': ['autocad', 'cad', 'revit', 'bim', '天正', 'sketchup', '3ds max',
               'photoshop', '效果图', '施工图', '建筑设计', '方案设计'],
    '结构工程': ['pkpm', 'sap2000', 'ansys', 'midas', '结构设计', '钢结构',
               '混凝土', '抗震', '岩土', '桥梁', '隧道'],
    '工程造价': ['广联达', '鲁班', '斯维尔', '工程量', '清单计价', '预算', '结算'],

    # 医疗/制药/生物
    '临床医学': ['临床', '诊断', '治疗', '手术', '内科', '外科', '儿科', '妇产科',
               '急诊', 'icu', '麻醉', '影像', '超声', '心电图'],
    '药学/制药': ['gmp', 'glp', '药典', '制剂', '药品注册', '临床研究', 'cra',
                '药物分析', '药理', '中药', '化学合成', 'fda', 'nda'],
    '护理': ['护理', '护士', '护师', '静脉', '无菌操作', '医嘱', '查房'],
    '生物技术': ['pcr', '细胞培养', '基因测序', '蛋白质', '生物信息', '酶联免疫',
               'western blot', 'elisa', '流式细胞', 'crispr'],

    # 教育/培训
    '教育教学': ['教学', '课程设计', '教案', '备课', '班主任', '学生管理',
               '教师资格证', '教师资格', '教育学', '心理学', '普通话'],
    '培训': ['培训', '课件', '企业培训', '新员工培训', '公开课', '线上教学'],

    # 设计/美术/创意
    '平面设计': ['photoshop', 'ps', 'illustrator', 'ai', 'coreldraw', 'indesign',
               '海报', '画册', 'vi', 'logo', '排版'],
    'UI/UX设计': ['figma', 'sketch', 'adobe xd', 'axure', '蓝湖', '墨刀',
                '用户研究', '交互设计', '原型', '界面设计'],
    '影视/动画': ['after effects', 'ae', 'premiere', 'pr', 'c4d', 'blender',
                'maya', '3d max', '剪辑', '特效', '动画', '达芬奇'],

    # 制造/工业/生产
    '机械设计': ['solidworks', 'proe', 'creo', 'ug', 'nx', 'catia', '机械设计',
               '钣金', '注塑', '模具设计', '公差', '尺寸链'],
    '电气/自动化': ['plc', '西门子', '三菱', '欧姆龙', '变频器', '伺服', 'scada',
                  'dcs', '电气设计', 'eplan', '电路', '配电'],
    '质量管理': ['iso9001', '六西格玛', 'spc', 'fmea', '质量体系', '精益生产',
               '5s', 'pdca', '8d报告', '质检'],

    # 法律/合规/知识产权
    '法律': ['合同法', '公司法', '劳动法', '知识产权', '专利', '商标', '诉讼',
            '仲裁', '法律文书', '尽调', '合规', '法务', '律师'],

    # 市场/运营/传媒
    '市场运营': ['seo', 'sem', '新媒体', '公众号', '短视频', '抖音', '直播',
               '社群运营', '用户运营', '活动策划', '品牌', '文案'],
    '市场营销': ['市场调研', '竞品分析', '营销策划', '广告投放', 'sem', '信息流',
               'kol', 'crm', '会员', '促销'],
    '电商': ['淘宝', '天猫', '京东', '拼多多', '亚马逊', 'shopee', '网店',
            '直通车', '钻展', '超级推荐', '跨境电商'],

    # 物流/供应链/仓储
    '物流供应链': ['供应链', '物流', '仓储', 'wms', 'tms', 'erp', '采购',
                 '库存管理', '配送', '国际物流', '货代', '报关'],
}

# ── 关键词 → 领域映射（用于根据搜索词自动推测领域）──
KEYWORD_TO_FIELD = {
    # IT
    'python': '计算机/IT', 'java': '计算机/IT', '前端': '计算机/IT', '后端': '计算机/IT',
    '开发': '计算机/IT', '程序员': '计算机/IT', '软件': '计算机/IT', '算法': '计算机/IT',
    '人工智能': '计算机/IT', '数据分析': '计算机/IT', '测试': '计算机/IT', '运维': '计算机/IT',

    # 金融
    '会计': '金融/会计', '财务': '金融/会计', '审计': '金融/会计', '税务': '金融/会计',
    '出纳': '金融/会计', 'cpa': '金融/会计', '金融': '金融/会计', '证券': '金融/会计',
    '银行': '金融/会计', '保险': '金融/会计', '风控': '金融/会计',

    # 建筑
    '建筑': '建筑/工程', '土木': '建筑/工程', '结构': '建筑/工程', '施工': '建筑/工程',
    '造价': '建筑/工程', 'bim': '建筑/工程', 'cad': '建筑/工程',

    # 医疗
    '医生': '医疗/制药', '护士': '医疗/制药', '临床': '医疗/制药', '药学': '医疗/制药',
    '制药': '医疗/制药', '医学': '医疗/制药', '中药': '医疗/制药', '生物': '医疗/制药',

    # 教育
    '教师': '教育/培训', '老师': '教育/培训', '教育': '教育/培训', '培训': '教育/培训',
    '讲师': '教育/培训', '课程': '教育/培训',

    # 设计
    '设计': '设计/美术', '美工': '设计/美术', 'ui': '设计/美术', '原画': '设计/美术',

    # 机械/制造
    '机械': '制造/工业', '电气': '制造/工业', '自动化': '制造/工业', '生产': '制造/工业',
    '质量': '制造/工业', '质检': '制造/工业', '数控': '制造/工业',

    # 法律
    '律师': '法律/合规', '法务': '法律/合规', '法律': '法律/合规', '合规': '法律/合规',

    # 市场
    '市场': '市场/运营', '运营': '市场/运营', '新媒体': '市场/运营', '电商': '市场/运营',
    '营销': '市场/运营', '直播': '市场/运营',

    # 物流
    '物流': '物流/供应链', '仓储': '物流/供应链', '供应链': '物流/供应链', '采购': '物流/供应链',
}

# ── 领域 → 优先匹配的技术栈类别 ──
FIELD_TO_CATEGORIES = {
    '计算机/IT': ['Python', 'Java', 'JavaScript/TS', '前端', '后端', '数据', 'AI/算法', '移动端', '运维/DevOps', '数据分析', '测试'],
    '金融/会计': ['财务会计', '金融分析', '数据分析'],
    '建筑/工程': ['建筑设计', '结构工程', '工程造价'],
    '医疗/制药': ['临床医学', '药学/制药', '护理', '生物技术'],
    '教育/培训': ['教育教学', '培训'],
    '设计/美术': ['平面设计', 'UI/UX设计', '影视/动画'],
    '制造/工业': ['机械设计', '电气/自动化', '质量管理'],
    '法律/合规': ['法律'],
    '市场/运营': ['市场运营', '市场营销', '电商'],
    '物流/供应链': ['物流供应链'],
}


def _load_custom_keywords():
    """从 config.yaml 加载自定义技术栈关键词"""
    try:
        import yaml
    except ImportError:
        return {}
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        custom = config.get('tech_keywords', {}).get('custom', {})
        return custom if isinstance(custom, dict) else {}
    except Exception:
        return {}


def detect_field_from_keyword(keyword: str) -> str:
    """根据搜索关键词自动推测所属领域"""
    kw = keyword.lower()
    for key, field in KEYWORD_TO_FIELD.items():
        if key in kw:
            return field
    return ''


def detect_tech_stack(title: str, description: str = "", keyword: str = "") -> list[str]:
    """从标题和描述中检测技术栈，可根据搜索关键词优先匹配对应领域"""
    text = (title + ' ' + description).lower()
    found = []

    # 合并自定义关键词
    all_keywords = dict(TECH_KEYWORDS)
    custom = _load_custom_keywords()
    for cat, kws in custom.items():
        all_keywords[cat] = kws

    # 根据搜索关键词推测领域，优先匹配对应类别
    field = detect_field_from_keyword(keyword)
    priority_categories = FIELD_TO_CATEGORIES.get(field, [])

    # 先检测优先领域
    for cat in priority_categories:
        if cat in all_keywords:
            for kw_word in all_keywords[cat]:
                if kw_word.lower() in text:
                    found.append(cat)
                    break

    # 再检测其他所有领域
    for category, keywords in all_keywords.items():
        if category in priority_categories:
            continue
        for kw_word in keywords:
            if kw_word.lower() in text:
                found.append(category)
                break

    return found


# ── 福利待遇关键词 ──
INSURANCE_KEYWORDS = ['五险一金', '六险一金', '五险', '六险', '社保', '公积金',
                       '七险一金', '五险二金', '补充医疗保险', '商业保险']

WEEKEND_OFF_KEYWORDS = ['双休', '周末双休', '周末休息', '双休制', '周休二日',
                         '做五休二', '不加班', '五天工作制', '工作日5天']

GRADUATE_KEYWORDS = ['应届生', '应届', '应届毕业生', '毕业生', '校招', '校园招聘',
                      '可接受应届', '接受应届', '欢迎应届', '面向应届',
                      '实习转正', '可转正', '管培生', '培训生', '接受无经验',
                      '不限经验', '无经验要求', '经验不限']


def detect_welfare(description: str, tags: str = "") -> dict:
    """从描述和标签中检测福利待遇"""
    text = (description + ' ' + tags).lower()
    has_insurance = any(kw.lower() in text for kw in INSURANCE_KEYWORDS)
    has_weekend_off = any(kw.lower() in text for kw in WEEKEND_OFF_KEYWORDS)
    is_accept_graduate = any(kw.lower() in text for kw in GRADUATE_KEYWORDS)
    return {
        'is_accept_graduate': is_accept_graduate,
        'has_weekend_off': has_weekend_off,
        'has_insurance': has_insurance,
    }
