#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 安装和配置脚本

这个脚本将帮助您：
1. 使用 Docker 启动 PostgreSQL 数据库
2. 安装必要的 Python 依赖
3. 初始化数据库表
4. 验证数据库连接
"""

import subprocess
import sys
import os
import time
import asyncio
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(f"输出: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        raise

def check_docker():
    """检查 Docker 是否安装"""
    try:
        result = run_command("docker --version", check=False)
        if result.returncode == 0:
            print("✓ Docker 已安装")
            return True
        else:
            print("✗ Docker 未安装")
            return False
    except Exception:
        print("✗ Docker 未安装")
        return False

def start_postgresql():
    """启动 PostgreSQL 容器"""
    print("\n=== 启动 PostgreSQL 数据库 ===")
    
    # 检查容器是否已经运行
    try:
        result = run_command("docker ps -q -f name=momoyu_postgres", check=False)
        if result.stdout.strip():
            print("PostgreSQL 容器已在运行")
            return True
    except Exception:
        pass
    
    # 检查容器是否存在但未运行
    try:
        result = run_command("docker ps -aq -f name=momoyu_postgres", check=False)
        if result.stdout.strip():
            print("启动现有的 PostgreSQL 容器...")
            run_command("docker start momoyu_postgres")
            time.sleep(5)
            return True
    except Exception:
        pass
    
    # 使用 docker-compose 启动
    print("使用 docker-compose 启动 PostgreSQL...")
    project_root = Path(__file__).parent
    run_command("docker-compose up -d postgres", cwd=project_root)
    
    # 等待数据库启动
    print("等待数据库启动...")
    time.sleep(10)
    
    return True

def install_dependencies():
    """安装 Python 依赖"""
    print("\n=== 安装 Python 依赖 ===")
    backend_dir = Path(__file__).parent / "backend"
    
    # 检查虚拟环境
    venv_dir = Path(__file__).parent / ".venv"
    if venv_dir.exists():
        if sys.platform == "win32":
            pip_cmd = str(venv_dir / "Scripts" / "pip.exe")
        else:
            pip_cmd = str(venv_dir / "bin" / "pip")
    else:
        pip_cmd = "pip"
    
    # 安装依赖
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        run_command(f"{pip_cmd} install -r {requirements_file}", cwd=backend_dir)
    else:
        print("requirements.txt 文件不存在")
        return False
    
    return True

async def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        # 添加项目路径
        backend_dir = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_dir))
        
        from app.core.database import engine, init_db
        
        # 测试连接
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✓ 数据库连接成功")
            print(f"PostgreSQL 版本: {version}")
        
        # 初始化数据库表
        print("初始化数据库表...")
        await init_db()
        print("✓ 数据库表初始化成功")
        
        # 关闭连接
        await engine.dispose()
        
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("PostgreSQL 数据库安装和配置向导")
    print("=" * 50)
    
    try:
        # 1. 检查 Docker
        if not check_docker():
            print("\n请先安装 Docker Desktop:")
            print("https://www.docker.com/products/docker-desktop/")
            return False
        
        # 2. 启动 PostgreSQL
        if not start_postgresql():
            print("PostgreSQL 启动失败")
            return False
        
        # 3. 安装依赖
        if not install_dependencies():
            print("依赖安装失败")
            return False
        
        # 4. 测试数据库连接
        success = asyncio.run(test_database_connection())
        
        if success:
            print("\n" + "=" * 50)
            print("✓ PostgreSQL 配置完成！")
            print("\n数据库信息:")
            print("  主机: localhost")
            print("  端口: 5432")
            print("  数据库: momoyu")
            print("  用户名: postgres")
            print("  密码: password")
            print("\n您现在可以启动应用程序了:")
            print("  cd backend")
            print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001")
        else:
            print("\n配置过程中出现错误，请检查日志")
            return False
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return False
    except Exception as e:
        print(f"\n配置过程中出现错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)