# Docker 构建优化指南

## 问题描述

在中国大陆地区，由于网络限制，Docker 构建时经常遇到以下问题：
- Python 基础镜像下载失败
- pip 包下载超时
- apt 包管理器更新失败

## 解决方案

### 1. 多镜像源智能构建

项目现在支持多个国内镜像源，自动尝试直到成功：

- **阿里云**：`registry.cn-hangzhou.aliyuncs.com/library/python:3.12-slim`
- **腾讯云**：`ccr.ccs.tencentyun.com/library/python:3.12-slim`
- **网易云**：`hub-mirror.c.163.com/library/python:3.12-slim`
- **华为云**：`swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.12-slim`
- **官方源**：`python:3.12-slim`（备用）

使用智能构建脚本 `build-backend.bat` 自动尝试所有镜像源。

#### 使用方法

1. **自动构建**（推荐）：
   ```bash
   # 直接运行启动脚本，会自动调用智能构建
   start.bat
   ```

2. **手动构建**：
   ```bash
   # 单独运行智能构建脚本
   build-backend.bat
   ```

3. **指定镜像源**：
   ```bash
   # 使用特定的 Dockerfile
   docker build -f backend/Dockerfile.tencent -t rebang-backend backend/
   ```

### 2. 多阶段构建

使用多阶段构建减少最终镜像大小：
- 构建阶段：安装依赖和编译
- 运行阶段：只包含运行时需要的文件

### 3. 备用构建方案

提供了 `Dockerfile.fallback` 作为备用方案：
- 使用官方 Python 镜像
- 简化的构建流程
- 更好的兼容性

### 4. 智能启动脚本

`start.bat` 脚本现在包含多层回退机制：
1. 尝试使用 docker-compose 启动
2. 如果失败，尝试使用备用 Dockerfile 构建
3. 如果仍然失败，回退到本地 Python 环境

## 手动解决方案

### 配置 Docker 镜像加速器

1. 打开 Docker Desktop
2. 进入 Settings > Docker Engine
3. 添加以下配置：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

### 使用备用 Dockerfile

如果主 Dockerfile 构建失败，可以手动使用备用版本：

```bash
# 构建备用镜像
docker build -f backend/Dockerfile.fallback -t rebang-backend-fallback backend/

# 运行备用容器
docker run -d --name rebang-backend-fallback -p 8000:8000 rebang-backend-fallback
```

### 本地环境运行

如果 Docker 完全无法使用，可以直接在本地运行：

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 性能优化建议

1. **使用 .dockerignore**：已创建 `.dockerignore` 文件排除不必要的文件
2. **缓存优化**：requirements.txt 单独复制，利用 Docker 层缓存
3. **安全性**：使用非 root 用户运行应用
4. **镜像大小**：多阶段构建减少最终镜像大小

## 故障排除

### 常见错误及解决方案

1. **网络超时**
   - 配置 Docker 镜像加速器
   - 使用备用 Dockerfile
   - 检查网络连接

2. **权限问题**
   - 确保 Docker Desktop 正在运行
   - 检查用户权限

3. **端口冲突**
   - 检查 8000 端口是否被占用
   - 使用 `netstat -ano | findstr :8000` 查看端口使用情况

## 监控和日志

查看容器日志：
```bash
# 查看 docker-compose 服务日志
docker-compose logs backend

# 查看备用容器日志
docker logs rebang-backend-fallback
```

查看容器状态：
```bash
docker ps -a
```