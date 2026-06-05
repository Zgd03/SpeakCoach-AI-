@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"

echo ========================================
echo  SpeakCoach AI - 启动前端服务
echo ========================================
echo.

:: Install dependencies if needed
if not exist "node_modules" (
    echo [*] 首次使用，安装依赖...
    call npm install
    echo.
)

echo [✓] 前端服务启动中...
echo     访问地址: http://localhost:5173
echo.
echo     按 Ctrl+C 停止服务
echo ========================================
echo.

call npm run dev

pause
