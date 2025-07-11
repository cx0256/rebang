# 热榜网站

基于 Nuxt 3 + FastAPI + PostgreSQL 构建的热榜聚合网站

## 技术栈

- **前端**: Nuxt 3 (Vue 3 + TypeScript)
- **后端**: FastAPI (Python)
- **数据库**: PostgreSQL
- **容器化**: Docker & Docker Compose

## 项目结构

```
momoyu/
├── frontend/          # Nuxt 3 前端项目
├── backend/           # FastAPI 后端项目
├── database/          # 数据库相关文件
├── docker-compose.yml # Docker 容器编排
└── README.md          # 项目说明
```

## 快速开始

### 🚀 一键启动（推荐）

#### Windows用户

##### 快速启动（推荐，仅启动数据库）
```bash
# PowerShell版本
.\quick-start.ps1
```

##### 完整自动启动
```bash
# 增强版本（自动启动Docker Desktop）
.\start-enhanced.bat

# 标准版本（需要手动启动Docker Desktop）
.\start.bat

# PowerShell版本
.\start.ps1
```

#### 故障排除

### Docker Desktop连接错误
如果遇到"open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified"错误：
- **原因**：Docker Desktop没有启动或服务未完全加载
- **解决方案**：
  1. **推荐**：使用 `./start-enhanced.bat` 自动启动Docker Desktop
  2. 手动启动Docker Desktop并等待完全加载
  3. 确保Docker Desktop在系统托盘中显示为绿色状态

### Docker Compose命令错误
如果遇到"no configuration file provided: not found"错误：
- **原因**：新版Docker Desktop使用`docker compose`（无连字符）
- **解决方案**：使用最新版本的启动脚本（已修复）

### 编码问题
如果遇到编码问题或乱码，请：
1. 确保使用管理员权限运行命令提示符
2. 使用PowerShell版本：`./quick-start.ps1`
3. 检查系统区域设置是否支持UTF-8

详细的故障排除指南请参考 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

#### 管理命令
```bash
# 查看服务状态
.\status.ps1

# 停止所有服务
.\stop.ps1
```

### 📋 前置要求
- Docker Desktop
- Node.js (>=18.0.0)
- Python (>=3.8)

### 🔧 手动启动

#### 1. 克隆项目
```bash
git clone <repository-url>
cd rebang
```

#### 2. 启动开发环境
```bash
# 启动数据库
docker compose up -d postgres redis

# 启动后端
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd ../frontend
npm install
npm run dev
```

#### 3. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 功能特性

- 多平台热榜聚合
- 实时数据更新
- 响应式设计
- RESTful API
- 数据持久化

## 开发计划

- [x] 项目初始化
- [ ] 数据库设计
- [ ] 后端API开发
- [ ] 前端页面开发
- [ ] 数据爬取模块
- [ ] 部署配置#   r e b a n g 
 
 