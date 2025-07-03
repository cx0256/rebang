# 热榜项目一键启动脚本
# PowerShell版本

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# 打印标题
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           热榜项目一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # 检查Docker
    Write-Host "[1/5] 检查Docker是否运行..." -ForegroundColor Yellow
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker未安装或未启动，请先安装并启动Docker" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "✅ Docker检查通过: $dockerVersion" -ForegroundColor Green

    # 检查Node.js
    Write-Host "[2/5] 检查Node.js环境..." -ForegroundColor Yellow
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Node.js未安装，请先安装Node.js (>=18.0.0)" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "✅ Node.js检查通过: $nodeVersion" -ForegroundColor Green

    # 检查Python
    Write-Host "[3/5] 检查Python环境..." -ForegroundColor Yellow
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python未安装，请先安装Python (>=3.8)" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "✅ Python检查通过: $pythonVersion" -ForegroundColor Green

    # 启动数据库服务
    Write-Host "[4/5] 启动数据库服务..." -ForegroundColor Yellow
    docker compose up -d postgres redis
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 数据库启动失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "✅ 数据库服务启动成功" -ForegroundColor Green

    # 等待数据库初始化
    Write-Host "等待数据库初始化..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
    Write-Host "✅ 数据库初始化完成" -ForegroundColor Green

    # 启动应用服务
    Write-Host "[5/5] 启动应用服务..." -ForegroundColor Yellow
    
    # 启动后端服务
    Write-Host "正在启动后端服务..." -ForegroundColor Cyan
    $backendScript = @"
Set-Location "$PWD\backend"
if (!(Test-Path ".venv")) {
    Write-Host "创建Python虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.venv\Scripts\Activate.ps1
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "启动后端服务..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@
    
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendScript) -WindowStyle Normal
    
    # 等待后端启动
    Write-Host "等待后端服务启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 12
    
    # 启动前端服务
    Write-Host "正在启动前端服务..." -ForegroundColor Cyan
    $frontendScript = @"
Set-Location "$PWD\frontend"
Write-Host "安装前端依赖..." -ForegroundColor Yellow
npm install
Write-Host "启动前端服务..." -ForegroundColor Green
npm run dev
"@
    
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendScript) -WindowStyle Normal
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "           启动完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "后端地址: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "提示: 关闭此窗口不会停止服务，如需停止请运行 stop.ps1" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ 启动过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

Read-Host "按Enter键退出"