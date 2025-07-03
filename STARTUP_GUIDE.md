# 🚀 热榜项目一键启动指南

## 📋 前置要求

在使用一键启动功能之前，请确保您的系统已安装以下软件：

### 必需软件
- **Docker Desktop** - 用于运行数据库服务
- **Node.js** (>=18.0.0) - 用于运行前端服务
- **Python** (>=3.8) - 用于运行后端服务

### 检查安装
```powershell
# 检查Docker
docker --version

# 检查Node.js
node --version

# 检查Python
python --version
```

## 🎯 使用方法

### 启动服务

#### 增强启动（推荐）
```cmd
# 自动启动Docker Desktop + 完整服务
.\start-enhanced.bat
```
**特点**：自动检测并启动Docker Desktop，等待服务完全加载后再启动项目服务

#### PowerShell启动
```powershell
# 快速启动（仅数据库）
.\quick-start.ps1

# 完整启动
.\start.ps1
```

#### 标准批处理启动
```cmd
# 完整启动（需要手动启动Docker Desktop）
start.bat
```

### 查看状态
```powershell
.\status.ps1
```

### 停止服务

#### PowerShell版本
```powershell
.\stop.ps1
```

#### 批处理版本
```cmd
stop.bat
```

## 📊 服务信息

启动成功后，您可以通过以下地址访问各个服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3000 | 用户界面 |
| 后端API | http://localhost:8000 | API服务 |
| API文档 | http://localhost:8000/docs | Swagger文档 |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存服务 |

## 🔧 启动流程

一键启动脚本会按以下顺序执行：

1. **环境检查** - 验证Docker、Node.js、Python是否已安装
2. **数据库启动** - 启动PostgreSQL和Redis容器
3. **后端启动** - 创建Python虚拟环境，安装依赖，启动FastAPI服务
4. **前端启动** - 安装Node.js依赖，启动Nuxt开发服务器

## ⚠️ 常见问题

### 1. Docker Desktop连接错误
**错误信息**: `error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.46/..." open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**原因分析**:
- Docker Desktop应用程序没有启动
- Docker Desktop正在启动但服务尚未完全加载
- Docker Desktop服务异常或崩溃

**解决方案**:
1. **自动解决（推荐）**：使用增强启动脚本
   ```bash
   ./start-enhanced.bat
   ```
   此脚本会自动检测并启动Docker Desktop，等待服务完全加载

2. **手动解决**：
   - 从开始菜单启动"Docker Desktop"
   - 等待系统托盘中Docker图标变为绿色
   - 确保Docker Desktop界面显示"Engine running"
   - 重新运行启动脚本

3. **验证Docker状态**：
   ```bash
   docker info
   ```
   如果返回Docker信息而非错误，说明Docker已正常运行

### 2. Docker Compose命令错误
**错误信息**: 出现 `no configuration file provided: not found` 错误

**解决方案**:
- **原因**：新版Docker Desktop使用`docker compose`（无连字符）而非`docker-compose`
- **解决方案**：确保使用最新版本的启动脚本，已更新为正确的命令格式
- **手动修复**：将所有`docker-compose`命令改为`docker compose`

### 2. 编码问题和乱码
**错误信息**: 出现类似 `'?..' 不是内部或外部命令` 或乱码字符

**解决方案**:
- 使用PowerShell版本：`./quick-start.ps1`
- 确保以管理员权限运行命令提示符
- 检查系统区域设置：控制面板 → 区域 → 管理 → 更改系统区域设置
- 如果问题持续，建议使用PowerShell而非批处理文件

### 3. Docker未启动
**错误信息**: `Docker未安装或未启动`

**解决方案**: 
- 确保Docker Desktop已安装并正在运行
- 检查Docker服务状态

### 4. 端口被占用
**错误信息**: 端口3000、8000、5432或6379被占用

**解决方案**:
```powershell
# 查看端口占用
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 结束占用进程（替换PID为实际进程ID）
taskkill /PID <PID> /F
```

### 5. Python虚拟环境问题
**解决方案**:
```powershell
# 删除现有虚拟环境
Remove-Item -Recurse -Force backend\.venv

# 重新运行启动脚本
.\start.ps1
```

### 6. Node.js依赖安装失败
**解决方案**:
```powershell
# 清理npm缓存
npm cache clean --force

# 删除node_modules
Remove-Item -Recurse -Force frontend\node_modules

# 重新安装
cd frontend
npm install
```

## 🛠️ 高级用法

### 仅启动数据库
```powershell
docker compose up -d postgres redis
```

### 仅启动后端
```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### 仅启动前端
```powershell
cd frontend
npm run dev
```

### 生产环境部署
```powershell
# 使用Docker Compose启动所有服务
docker compose --profile production up -d
```

## 📝 日志查看

### Docker容器日志
```powershell
# 查看所有容器日志
docker compose logs

# 查看特定容器日志
docker compose logs postgres
docker compose logs redis
```

### 应用日志
- 后端日志：在后端启动窗口中查看
- 前端日志：在前端启动窗口中查看

## 🔄 更新项目

当项目代码更新后：

1. 停止所有服务：`./stop.ps1`
2. 拉取最新代码：`git pull`
3. 重新启动：`./start.ps1`

## 💡 提示

- 首次启动可能需要较长时间，因为需要下载Docker镜像和安装依赖
- 建议使用PowerShell版本的脚本，功能更完整
- 关闭启动脚本窗口不会停止服务，需要运行stop脚本
- 可以使用status脚本随时查看服务运行状态

---

如有问题，请查看项目README.md或提交Issue。