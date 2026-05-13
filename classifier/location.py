import re

TIER_MAP = {
    '一线': ['北京', '上海', '广州', '深圳'],
    '新一线': ['杭州', '成都', '武汉', '南京', '重庆', '苏州', '西安',
              '长沙', '天津', '郑州', '东莞', '青岛', '合肥', '佛山', '宁波'],
    '二线': ['昆明', '沈阳', '济南', '无锡', '厦门', '福州', '温州', '大连',
            '哈尔滨', '长春', '泉州', '石家庄', '贵阳', '南昌', '太原',
            '南宁', '海口', '兰州', '银川', '西宁', '呼和浩特', '乌鲁木齐',
            '拉萨', '珠海', '惠州', '中山', '嘉兴', '绍兴', '金华', '台州',
            '烟台', '潍坊', '洛阳', '唐山'],
}


def classify_location(raw_location: str) -> tuple[str, str]:
    """
    解析地点，返回 (城市名, 城市等级)
    例: '北京·海淀区' -> ('北京', '一线')
    """
    if not raw_location:
        return '', '其他'

    text = raw_location.strip()

    # 远程判断
    if re.search(r'远程|remote', text, re.IGNORECASE):
        return '远程', '远程'

    # 尝试匹配城市
    for tier, cities in TIER_MAP.items():
        for city in cities:
            if city in text:
                return city, tier

    # 提取前2-3个字尝试匹配
    short = text[:3]
    for tier, cities in TIER_MAP.items():
        for city in cities:
            if short in city or city[:2] in short:
                return city, tier

    return text[:10], '其他'
