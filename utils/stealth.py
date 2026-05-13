import random

STEALTH_SCRIPTS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
window.chrome = {runtime: {}};
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]


def get_random_ua() -> str:
    return random.choice(USER_AGENTS)


async def create_stealth_context(browser, headless: bool = True):
    """创建带反检测措施的浏览器上下文"""
    context = await browser.new_context(
        user_agent=get_random_ua(),
        viewport={
            "width": random.randint(1366, 1920),
            "height": random.randint(720, 1080),
        },
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    await context.add_init_script(STEALTH_SCRIPTS)
    return context


async def simulate_human(page):
    """模拟人类浏览行为"""
    # 随机滚动
    await page.evaluate("window.scrollBy(0, {})".format(random.randint(200, 600)))
    await page.wait_for_timeout(random.randint(500, 1500))
    # 随机鼠标移动
    await page.mouse.move(
        random.randint(100, 800),
        random.randint(100, 500),
        steps=random.randint(3, 8),
    )
