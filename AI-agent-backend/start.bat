@echo off
REM AI Agent Backend 快速启动脚本

echo ========================================
echo    AI Agent Backend 启动脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo 1. 检查Python环境... ✓

REM 检查依赖
echo 2. 检查依赖...
pip show fastapi >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 安装依赖中...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)
echo    依赖检查完成 ✓

REM 初始化数据库
echo 3. 初始化数据库...
python scripts/init_db.py
if %ERRORLEVEL% NEQ 0 (
    echo 警告: 数据库初始化失败，但应用可能仍可运行
)
echo    数据库初始化完成 ✓

REM 启动应用
echo 4. 启动应用...
echo.
echo ========================================
echo 应用启动中...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo ========================================
echo.
echo 按 Ctrl+C 停止应用
echo.

python main.py
