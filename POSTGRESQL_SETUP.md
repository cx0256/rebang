# PostgreSQL 数据库设置指南

本指南将帮助您将项目从 SQLite 迁移到 PostgreSQL 数据库。

## 前置要求

- Docker Desktop (推荐) 或本地 PostgreSQL 安装
- Python 3.8+
- 项目依赖已安装

## 方法一：使用 Docker (推荐)

### 1. 安装 Docker Desktop

如果您还没有安装 Docker，请从官网下载并安装：
- Windows/Mac: https://www.docker.com/products/docker-desktop/
- Linux: 使用包管理器安装 docker 和 docker-compose

### 2. 自动设置 (推荐)

运行自动设置脚本：

```bash
python setup_postgresql.py
```

这个脚本将：
- 检查 Docker 是否安装
- 启动 PostgreSQL 容器
- 安装必要的 Python 依赖
- 初始化数据库表
- 验证数据库连接

### 3. 手动设置

如果自动设置失败，您可以手动执行以下步骤：

#### 3.1 启动 PostgreSQL 容器

```bash
# 启动 PostgreSQL 和 Redis
docker-compose up -d postgres redis

# 查看容器状态
docker-compose ps
```

#### 3.2 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3.3 初始化数据库

```bash
cd backend
python init_db_only.py
```

## 方法二：本地 PostgreSQL 安装

### 1. 安装 PostgreSQL

#### Windows
- 下载并安装：https://www.postgresql.org/download/windows/
- 记住设置的密码

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. 创建数据库和用户

```bash
# 连接到 PostgreSQL
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE momoyu;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE momoyu TO postgres;
\q
```

### 3. 更新配置

确保 `backend/.env` 文件中的数据库 URL 正确：

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/momoyu
```

### 4. 安装依赖并初始化

```bash
cd backend
pip install -r requirements.txt
python init_db_only.py
```

## 数据迁移

如果您之前使用 SQLite 并有数据需要迁移：

```bash
cd backend
python migrate_to_postgresql.py
```

这个脚本将：
- 从现有的 SQLite 数据库读取数据
- 将数据迁移到 PostgreSQL
- 验证迁移结果

## 验证设置

### 1. 测试数据库连接

```bash
cd backend
python -c "import asyncio; from app.core.database import engine; asyncio.run(engine.dispose())"
```

### 2. 启动应用

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 3. 测试 API

访问 http://localhost:8001/docs 查看 API 文档

## 数据库配置说明

### 连接信息

- **主机**: localhost
- **端口**: 5432
- **数据库**: momoyu
- **用户名**: postgres
- **密码**: password

### 环境变量

在 `backend/.env` 文件中配置：

```env
# PostgreSQL 配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/momoyu
DATABASE_ECHO=false
```

### Docker Compose 配置

PostgreSQL 容器配置在 `docker-compose.yml` 中：

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: momoyu
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
```

## 常见问题

### 1. 连接被拒绝

**错误**: `connection refused`

**解决方案**:
- 确保 PostgreSQL 服务正在运行
- 检查端口 5432 是否被占用
- 验证防火墙设置

### 2. 认证失败

**错误**: `authentication failed`

**解决方案**:
- 检查用户名和密码是否正确
- 确保用户有访问数据库的权限

### 3. 数据库不存在

**错误**: `database "momoyu" does not exist`

**解决方案**:
- 手动创建数据库或重新运行初始化脚本
- 检查 Docker 容器是否正确启动

### 4. 依赖安装失败

**错误**: `asyncpg` 或其他依赖安装失败

**解决方案**:
```bash
# 更新 pip
pip install --upgrade pip

# 安装构建工具 (Windows)
pip install wheel setuptools

# 重新安装依赖
pip install -r requirements.txt
```

## 性能优化

### 1. 连接池配置

在 `app/core/database.py` 中已配置连接池：

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=0,        # 最大溢出连接
    pool_pre_ping=True,    # 连接前测试
    pool_recycle=3600,     # 连接回收时间
)
```

### 2. 索引优化

数据库初始化脚本 `database/init.sql` 包含了必要的索引。

### 3. 查询优化

- 使用异步查询
- 适当的分页
- 避免 N+1 查询问题

## 备份和恢复

### 备份数据库

```bash
# 使用 Docker
docker exec momoyu_postgres pg_dump -U postgres momoyu > backup.sql

# 本地安装
pg_dump -U postgres -h localhost momoyu > backup.sql
```

### 恢复数据库

```bash
# 使用 Docker
docker exec -i momoyu_postgres psql -U postgres momoyu < backup.sql

# 本地安装
psql -U postgres -h localhost momoyu < backup.sql
```

## 监控和维护

### 1. 查看连接状态

```sql
SELECT * FROM pg_stat_activity WHERE datname = 'momoyu';
```

### 2. 查看数据库大小

```sql
SELECT pg_size_pretty(pg_database_size('momoyu'));
```

### 3. 查看表大小

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 下一步

设置完成后，您可以：

1. 启动后端服务：`cd backend && python -m uvicorn app.main:app --reload`
2. 启动前端服务：`cd frontend && npm run dev`
3. 运行爬虫：`cd backend && python run_crawler_and_save.py`
4. 查看 API 文档：http://localhost:8001/docs

如果遇到问题，请检查日志文件或提交 Issue。