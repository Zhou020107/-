@echo off
chcp 65001 >nul
echo ============================================
echo   职位爬虫工具 - 一键安装
echo ============================================
echo.

echo [1/3] 安装 Python 依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo 清华镜像安装失败, 尝试默认源...
    pip install -r requirements.txt
)

echo [2/3] 安装 Playwright 浏览器...
python -m playwright install chromium

echo [3/3] 初始化数据库...
python -c "from storage.database import Database; Database().init()"

echo.
echo ============================================
echo   安装完成!
echo   运行命令: streamlit run app.py
echo ============================================
pause
