# Copyright (c) 2025 左岚. All rights reserved.
# Stagewise 集成启动脚本

Write-Host "🚀 启动 AI Agent 测试平台 + Stagewise 集成..." -ForegroundColor Green

# 检查依赖
Write-Host "📋 检查依赖..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js 未安装，请先安装 Node.js" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 未安装，请先安装 Python" -ForegroundColor Red
    exit 1
}

# 检查端口占用
Write-Host "🔍 检查端口占用..." -ForegroundColor Yellow
$ports = @(3100, 5173, 8000)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠️  端口 $port 已被占用，请先关闭相关进程" -ForegroundColor Yellow
    }
}

# 启动后端服务
Write-Host "🔧 启动后端服务..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '..\AI-agent-backend'; python main.py" -WindowStyle Normal

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "🎨 启动前端服务..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

# 等待前端启动
Start-Sleep -Seconds 5

# 启动 Stagewise
Write-Host "🤖 启动 Stagewise AI 助手..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx stagewise --silent" -WindowStyle Normal

Write-Host ""
Write-Host "✅ 所有服务启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📍 访问地址：" -ForegroundColor White
Write-Host "   前端应用: http://localhost:5173/" -ForegroundColor Cyan
Write-Host "   后端 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Stagewise: http://localhost:3100" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 使用说明：请查看 STAGEWISE_INTEGRATION_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
