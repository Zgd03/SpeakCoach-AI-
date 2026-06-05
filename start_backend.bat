@echo off
chcp 65001 >nul
cd /d "%~dp0backend"

echo ========================================
echo  SpeakCoach AI - 启动后端服务
echo ========================================
echo.

:: Check if .env has API key
findstr /C:"DEEPSEEK_API_KEY=" ..\.env >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 未找到 .env 文件，请先创建并配置 API Key
    echo     参考 .env.example
    echo.
)

:: Install dependencies if needed
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [*] 首次使用，安装依赖...
    pip install -r requirements.txt
    echo.
)

:: Seed database if needed
python -m app.seed
echo.

echo [✓] 后端服务启动中...
echo     访问地址: http://localhost:8000
echo     API 文档: http://localhost:8000/docs
echo.
echo     按 Ctrl+C 停止服务
echo ========================================
echo.

uvicorn app.main:app --reload --port 8000

pause
