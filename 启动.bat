@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   正在启动职位信息采集工具...
echo ============================================
echo.
echo   启动后请用浏览器打开:
echo   电脑端: http://localhost:8501
echo   手机端: 同一WiFi下访问侧边栏显示的IP地址
echo.
echo   按 Ctrl+C 可以停止程序
echo ============================================
echo.
streamlit run app.py
pause
