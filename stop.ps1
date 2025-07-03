# 热榜项目停止脚本
# PowerShell版本

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 打印标题
Write-Host "========================================" -ForegroundColor Red
Write-Host "           热榜项目停止服务" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

try {
    # 停止Docker容器
    Write-Host "[1/3] 停止数据库服务..." -ForegroundColor Yellow
    docker compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 数据库服务已停止" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 数据库服务停止时出现警告" -ForegroundColor Yellow
    }

    # 停止Node.js进程
    Write-Host "[2/3] 停止前端服务..." -ForegroundColor Yellow
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        $nodeProcesses | ForEach-Object {
            try {
                Stop-Process -Id $_.Id -Force
                Write-Host "✅ 已停止Node.js进程 (PID: $($_.Id))" -ForegroundColor Green
            } catch {
                Write-Host "⚠️ 无法停止Node.js进程 (PID: $($_.Id))" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "ℹ️ 没有找到运行中的Node.js进程" -ForegroundColor Cyan
    }

    # 停止Python/uvicorn进程
    Write-Host "[3/3] 停止后端服务..." -ForegroundColor Yellow
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | ForEach-Object {
            # 检查是否是uvicorn进程
            $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
            if ($commandLine -and $commandLine -like "*uvicorn*") {
                try {
                    Stop-Process -Id $_.Id -Force
                    Write-Host "✅ 已停止Python/uvicorn进程 (PID: $($_.Id))" -ForegroundColor Green
                } catch {
                    Write-Host "⚠️ 无法停止Python进程 (PID: $($_.Id))" -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host "ℹ️ 没有找到运行中的Python进程" -ForegroundColor Cyan
    }

    # 检查端口占用
    Write-Host ""
    Write-Host "检查端口占用情况..." -ForegroundColor Yellow
    
    $ports = @(3000, 8000, 5432, 6379)
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "⚠️ 端口 $port 仍被占用" -ForegroundColor Yellow
        } else {
            Write-Host "✅ 端口 $port 已释放" -ForegroundColor Green
        }
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "           停止完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "所有服务已停止。如需重新启动，请运行 start.ps1" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ 停止过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "按Enter键退出"