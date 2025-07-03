#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的 PostgreSQL 启动脚本

这个脚本提供多种方式启动 PostgreSQL：
1. Docker Desktop (如果已安装并运行)
2. 本地 PostgreSQL 安装指导
3. 便携式 PostgreSQL 下载和配置
"""

import subprocess
import sys
import os
import time
import asyncio
import urllib.request
import zipfile
from pathlib import Path

def run_command(command, cwd=None, check=True, capture_output=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True,
            encoding='utf-8'
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"命令执行失败: {e}")
            if e.stderr:
                print(f"错误: {e.stderr}")
        return e
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return None

def check_docker_desktop():
    """检查 Docker Desktop 是否运行"""
    print("检查 Docker Desktop 状态...")
    
    # 检查 Docker 是否安装
    result = run_command("docker --version", check=False)
    if isinstance(result, subprocess.CalledProcessError) or result is None:
        return False, "Docker 未安装"
    
    # 检查 Docker 是否运行
    result = run_command("docker info", check=False)
    if isinstance(result, subprocess.CalledProcessError):
        return False, "Docker Desktop 未运行"
    
    return True, "Docker Desktop 正常运行"

def start_docker_postgresql():
    """使用 Docker 启动 PostgreSQL"""
    print("\n=== 使用 Docker 启动 PostgreSQL ===")
    
    # 检查是否已有容器运行
    result = run_command("docker ps -q -f name=momoyu_postgres", check=False)
    if result and result.stdout.strip():
        print("✓ PostgreSQL 容器已在运行")
        return True
    
    # 检查是否有停止的容器
    result = run_command("docker ps -aq -f name=momoyu_postgres", check=False)
    if result and result.stdout.strip():
        print("启动现有的 PostgreSQL 容器...")
        result = run_command("docker start momoyu_postgres", check=False)
        if not isinstance(result, subprocess.CalledProcessError):
            print("✓ PostgreSQL 容器启动成功")
            return True
    
    # 创建新容器
    print("创建新的 PostgreSQL 容器...")
    docker_cmd = (
        "docker run -d "
        "--name momoyu_postgres "
        "-e POSTGRES_DB=momoyu "
        "-e POSTGRES_USER=postgres "
        "-e POSTGRES_PASSWORD=password "
        "-p 5432:5432 "
        "postgres:15"
    )
    
    result = run_command(docker_cmd, check=False)
    if isinstance(result, subprocess.CalledProcessError):
        print(f"✗ 创建容器失败: {result.stderr}")
        return False
    
    print("✓ PostgreSQL 容器创建成功")
    print("等待数据库启动...")
    time.sleep(10)
    
    return True

def download_portable_postgresql():
    """下载便携式 PostgreSQL"""
    print("\n=== 下载便携式 PostgreSQL ===")
    
    postgres_dir = Path("postgresql_portable")
    if postgres_dir.exists():
        print("✓ 便携式 PostgreSQL 已存在")
        return postgres_dir
    
    print("下载 PostgreSQL 便携版...")
    print("注意: 这可能需要几分钟时间")
    
    # PostgreSQL 便携版下载链接 (示例)
    # 实际使用时应该使用官方链接
    url = "https://get.enterprisedb.com/postgresql/postgresql-15.4-1-windows-x64-binaries.zip"
    
    try:
        # 创建目录
        postgres_dir.mkdir(exist_ok=True)
        
        # 下载文件
        zip_file = postgres_dir / "postgresql.zip"
        print(f"正在下载到: {zip_file}")
        
        # 这里只是示例，实际下载需要处理大文件
        print("由于文件较大，请手动下载 PostgreSQL:")
        print("1. 访问: https://www.postgresql.org/download/windows/")
        print("2. 下载 PostgreSQL 15 Windows 版本")
        print("3. 安装到默认位置")
        print("4. 记住设置的密码")
        
        return None
        
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def check_local_postgresql():
    """检查本地 PostgreSQL 安装"""
    print("\n=== 检查本地 PostgreSQL ===")
    
    # 常见的 PostgreSQL 安装路径
    possible_paths = [
        r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\13\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\14\bin\psql.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ 找到 PostgreSQL: {path}")
            return path
    
    # 检查 PATH 中的 psql
    result = run_command("psql --version", check=False)
    if result and not isinstance(result, subprocess.CalledProcessError):
        print("✓ PostgreSQL 在系统 PATH 中")
        return "psql"
    
    print("✗ 未找到本地 PostgreSQL 安装")
    return None

def create_database_local(psql_path):
    """在本地 PostgreSQL 中创建数据库"""
    print("\n=== 创建数据库 ===")
    
    # 创建数据库的 SQL 命令
    sql_commands = [
        "CREATE DATABASE momoyu;",
        "CREATE USER momoyu_user WITH PASSWORD 'password';",
        "GRANT ALL PRIVILEGES ON DATABASE momoyu TO momoyu_user;",
        "ALTER USER momoyu_user CREATEDB;"
    ]
    
    print("请手动执行以下步骤:")
    print("1. 打开命令提示符或 PowerShell")
    print("2. 连接到 PostgreSQL:")
    print(f"   {psql_path} -U postgres")
    print("3. 输入 PostgreSQL 安装时设置的密码")
    print("4. 执行以下 SQL 命令:")
    
    for cmd in sql_commands:
        print(f"   {cmd}")
    
    print("5. 输入 \\q 退出")
    
    input("\n完成后按 Enter 继续...")

async def test_connection(database_url):
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        # 添加项目路径
        backend_dir = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_dir))
        
        # 临时设置数据库 URL
        os.environ['DATABASE_URL'] = database_url
        
        from app.core.database import engine
        from sqlalchemy import text
        
        # 测试连接
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ 数据库连接成功")
            print(f"PostgreSQL 版本: {version}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def update_env_file(database_url):
    """更新 .env 文件"""
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("✗ .env 文件不存在")
        return False
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新 DATABASE_URL
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f'DATABASE_URL={database_url}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'DATABASE_URL={database_url}\n')
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✓ 已更新 .env 文件: {database_url}")
    return True

def main():
    """主函数"""
    print("PostgreSQL 数据库启动向导")
    print("=" * 50)
    
    database_url = None
    
    # 方法1: 尝试 Docker
    docker_ok, docker_msg = check_docker_desktop()
    print(f"Docker 状态: {docker_msg}")
    
    if docker_ok:
        print("\n选择启动方式:")
        print("1. 使用 Docker (推荐)")
        print("2. 使用本地 PostgreSQL")
        print("3. 下载便携式 PostgreSQL")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == '1':
            if start_docker_postgresql():
                database_url = "postgresql+asyncpg://postgres:password@localhost:5432/momoyu"
        elif choice == '2':
            psql_path = check_local_postgresql()
            if psql_path:
                create_database_local(psql_path)
                database_url = "postgresql+asyncpg://postgres:password@localhost:5432/momoyu"
            else:
                print("请先安装 PostgreSQL")
                return False
        elif choice == '3':
            download_portable_postgresql()
            return False
    else:
        print("\n由于 Docker 不可用，检查本地 PostgreSQL...")
        psql_path = check_local_postgresql()
        if psql_path:
            create_database_local(psql_path)
            database_url = "postgresql+asyncpg://postgres:password@localhost:5432/momoyu"
        else:
            print("\n请选择以下方式之一:")
            print("1. 安装 Docker Desktop: https://www.docker.com/products/docker-desktop/")
            print("2. 安装 PostgreSQL: https://www.postgresql.org/download/windows/")
            print("3. 使用在线 PostgreSQL 服务 (如 ElephantSQL, Supabase)")
            return False
    
    if database_url:
        # 更新配置文件
        update_env_file(database_url)
        
        # 测试连接
        success = asyncio.run(test_connection(database_url))
        
        if success:
            print("\n" + "=" * 50)
            print("✓ PostgreSQL 配置完成！")
            print("\n下一步:")
            print("1. 安装依赖: cd backend && pip install -r requirements.txt")
            print("2. 初始化数据库: cd backend && python init_db_only.py")
            print("3. 启动应用: cd backend && python -m uvicorn app.main:app --reload")
            return True
        else:
            print("\n配置失败，请检查数据库设置")
            return False
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n如需帮助，请查看 POSTGRESQL_SETUP.md 文档")
    sys.exit(0 if success else 1)