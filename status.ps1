# 热榜项目状态检查脚本
# PowerShell版本

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 打印标题
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           热榜项目状态检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker容器状态
Write-Host "📦 Docker容器状态:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
try {
    $containers = docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>$null
    if ($LASTEXITCODE -eq 0 -and $containers) {
        $containers | ForEach-Object {
            if ($_ -match "Up") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "Exit") {
                Write-Host $_ -ForegroundColor Red
            } else {
                Write-Host $_
            }
        }
    } else {
        Write-Host "ℹ️ 没有运行中的Docker容器" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ 无法获取Docker容器状态" -ForegroundColor Red
}

Write-Host ""

# 检查端口占用情况
Write-Host "🌐 端口占用状态:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$services = @(
    @{Name="前端服务"; Port=3000; Url="http://localhost:3000"},
    @{Name="后端服务"; Port=8000; Url="http://localhost:8000"},
    @{Name="PostgreSQL"; Port=5432; Url="localhost:5432"},
    @{Name="Redis"; Port=6379; Url="localhost:6379"}
)

foreach ($service in $services) {
    $connection = Get-NetTCPConnection -LocalPort $service.Port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "✅ $($service.Name) (端口 $($service.Port)) - 运行中" -ForegroundColor Green
        if ($service.Port -in @(3000, 8000)) {
            Write-Host "   🔗 访问地址: $($service.Url)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ $($service.Name) (端口 $($service.Port)) - 未运行" -ForegroundColor Red
    }
}

Write-Host ""

# 检查进程状态
Write-Host "⚙️ 进程状态:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# 检查Node.js进程
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "✅ Node.js进程: $($nodeProcesses.Count) 个" -ForegroundColor Green
    $nodeProcesses | ForEach-Object {
        Write-Host "   PID: $($_.Id), CPU: $([math]::Round($_.CPU, 2))s, 内存: $([math]::Round($_.WorkingSet64/1MB, 2))MB" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Node.js进程: 未运行" -ForegroundColor Red
}

# 检查Python进程
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $uvicornProcesses = $pythonProcesses | Where-Object {
        $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        $commandLine -and $commandLine -like "*uvicorn*"
    }
    if ($uvicornProcesses) {
        Write-Host "✅ Python/uvicorn进程: $($uvicornProcesses.Count) 个" -ForegroundColor Green
        $uvicornProcesses | ForEach-Object {
            Write-Host "   PID: $($_.Id), CPU: $([math]::Round($_.CPU, 2))s, 内存: $([math]::Round($_.WorkingSet64/1MB, 2))MB" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Python/uvicorn进程: 未运行" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Python进程: 未运行" -ForegroundColor Red
}

Write-Host ""

# 服务健康检查
Write-Host "🏥 服务健康检查:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# 检查后端API健康状态
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    if ($response.status -eq "healthy") {
        Write-Host "✅ 后端API: 健康" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 后端API: 响应异常" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 后端API: 无法连接" -ForegroundColor Red
}

# 检查前端服务
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Head -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端服务: 正常" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 前端服务: 响应异常 (状态码: $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 前端服务: 无法连接" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           检查完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示:" -ForegroundColor Yellow
Write-Host "   - 启动服务: .\start.ps1" -ForegroundColor Cyan
Write-Host "   - 停止服务: .\stop.ps1" -ForegroundColor Cyan
Write-Host "   - 查看状态: .\status.ps1" -ForegroundColor Cyan
Write-Host ""

Read-Host "按Enter键退出"