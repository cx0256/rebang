#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：从 SQLite 迁移到 PostgreSQL

这个脚本将：
1. 从现有的 SQLite 数据库读取数据
2. 将数据迁移到 PostgreSQL 数据库
3. 验证迁移结果
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import sqlite3
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, AsyncSessionLocal
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class DatabaseMigrator:
    def __init__(self, sqlite_db_path: str):
        self.sqlite_db_path = sqlite_db_path
        self.migration_stats = {
            'platforms': 0,
            'categories': 0,
            'hot_items': 0,
            'errors': []
        }
    
    def read_sqlite_data(self) -> Dict[str, List[Dict]]:
        """从 SQLite 数据库读取数据"""
        if not os.path.exists(self.sqlite_db_path):
            print(f"SQLite 数据库文件不存在: {self.sqlite_db_path}")
            return {'platforms': [], 'categories': [], 'hot_items': []}
        
        conn = sqlite3.connect(self.sqlite_db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        
        data = {'platforms': [], 'categories': [], 'hot_items': []}
        
        try:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"SQLite 数据库中的表: {tables}")
            
            # 读取平台数据
            if 'platforms' in tables:
                cursor.execute("SELECT * FROM platforms")
                data['platforms'] = [dict(row) for row in cursor.fetchall()]
                print(f"读取到 {len(data['platforms'])} 个平台")
            
            # 读取分类数据
            if 'categories' in tables:
                cursor.execute("SELECT * FROM categories")
                data['categories'] = [dict(row) for row in cursor.fetchall()]
                print(f"读取到 {len(data['categories'])} 个分类")
            
            # 读取热榜项目数据
            if 'hot_items' in tables:
                cursor.execute("SELECT * FROM hot_items ORDER BY created_at DESC LIMIT 1000")
                data['hot_items'] = [dict(row) for row in cursor.fetchall()]
                print(f"读取到 {len(data['hot_items'])} 个热榜项目")
        
        except Exception as e:
            print(f"读取 SQLite 数据时出错: {e}")
            self.migration_stats['errors'].append(f"SQLite 读取错误: {e}")
        
        finally:
            conn.close()
        
        return data
    
    async def migrate_platforms(self, session: AsyncSession, platforms: List[Dict]):
        """迁移平台数据"""
        for platform_data in platforms:
            try:
                # 检查平台是否已存在
                existing = await session.execute(
                    text("SELECT id FROM platforms WHERE name = :name"),
                    {'name': platform_data['name']}
                )
                if existing.scalar():
                    continue
                
                platform = Platform(
                    name=platform_data['name'],
                    display_name=platform_data.get('display_name', platform_data['name']),
                    base_url=platform_data.get('base_url'),
                    icon_url=platform_data.get('icon_url'),
                    description=platform_data.get('description'),
                    is_active=platform_data.get('is_active', True)
                )
                session.add(platform)
                self.migration_stats['platforms'] += 1
                
            except Exception as e:
                error_msg = f"迁移平台 {platform_data.get('name', 'unknown')} 时出错: {e}"
                print(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        await session.commit()
    
    async def migrate_categories(self, session: AsyncSession, categories: List[Dict]):
        """迁移分类数据"""
        for category_data in categories:
            try:
                # 检查分类是否已存在
                existing = await session.execute(
                    text("SELECT id FROM categories WHERE platform_id = :platform_id AND name = :name"),
                    {
                        'platform_id': category_data['platform_id'],
                        'name': category_data['name']
                    }
                )
                if existing.scalar():
                    continue
                
                category = Category(
                    platform_id=category_data['platform_id'],
                    name=category_data['name'],
                    display_name=category_data.get('display_name', category_data['name']),
                    api_endpoint=category_data.get('api_endpoint'),
                    is_active=category_data.get('is_active', True)
                )
                session.add(category)
                self.migration_stats['categories'] += 1
                
            except Exception as e:
                error_msg = f"迁移分类 {category_data.get('name', 'unknown')} 时出错: {e}"
                print(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        await session.commit()
    
    async def migrate_hot_items(self, session: AsyncSession, hot_items: List[Dict]):
        """迁移热榜项目数据"""
        batch_size = 100
        for i in range(0, len(hot_items), batch_size):
            batch = hot_items[i:i + batch_size]
            
            for item_data in batch:
                try:
                    # 检查项目是否已存在
                    existing = await session.execute(
                        text("SELECT id FROM hot_items WHERE url = :url AND created_at = :created_at"),
                        {
                            'url': item_data['url'],
                            'created_at': item_data['created_at']
                        }
                    )
                    if existing.scalar():
                        continue
                    
                    hot_item = HotItem(
                        category_id=item_data['category_id'],
                        title=item_data['title'],
                        url=item_data['url'],
                        description=item_data.get('description'),
                        rank=item_data.get('rank'),
                        score=item_data.get('score'),
                        comment_count=item_data.get('comment_count'),
                        author=item_data.get('author'),
                        tags=item_data.get('tags'),
                        extra_data=item_data.get('extra_data')
                    )
                    
                    # 处理时间字段
                    if 'created_at' in item_data and item_data['created_at']:
                        if isinstance(item_data['created_at'], str):
                            hot_item.created_at = datetime.fromisoformat(item_data['created_at'].replace('Z', '+00:00'))
                        else:
                            hot_item.created_at = item_data['created_at']
                    
                    session.add(hot_item)
                    self.migration_stats['hot_items'] += 1
                    
                except Exception as e:
                    error_msg = f"迁移热榜项目 {item_data.get('title', 'unknown')} 时出错: {e}"
                    print(error_msg)
                    self.migration_stats['errors'].append(error_msg)
            
            # 批量提交
            await session.commit()
            print(f"已迁移 {min(i + batch_size, len(hot_items))}/{len(hot_items)} 个热榜项目")
    
    async def verify_migration(self, session: AsyncSession):
        """验证迁移结果"""
        print("\n=== 验证迁移结果 ===")
        
        # 统计 PostgreSQL 中的数据
        platforms_count = await session.execute(text("SELECT COUNT(*) FROM platforms"))
        categories_count = await session.execute(text("SELECT COUNT(*) FROM categories"))
        hot_items_count = await session.execute(text("SELECT COUNT(*) FROM hot_items"))
        
        print(f"PostgreSQL 中的数据统计:")
        print(f"  平台: {platforms_count.scalar()}")
        print(f"  分类: {categories_count.scalar()}")
        print(f"  热榜项目: {hot_items_count.scalar()}")
    
    async def run_migration(self):
        """执行完整的迁移过程"""
        print("开始数据库迁移...")
        print(f"源数据库: {self.sqlite_db_path}")
        
        # 1. 读取 SQLite 数据
        print("\n=== 读取 SQLite 数据 ===")
        data = self.read_sqlite_data()
        
        if not any(data.values()):
            print("没有找到需要迁移的数据")
            return
        
        # 2. 迁移到 PostgreSQL
        print("\n=== 迁移到 PostgreSQL ===")
        async with AsyncSessionLocal() as session:
            try:
                # 迁移平台
                if data['platforms']:
                    print("迁移平台数据...")
                    await self.migrate_platforms(session, data['platforms'])
                
                # 迁移分类
                if data['categories']:
                    print("迁移分类数据...")
                    await self.migrate_categories(session, data['categories'])
                
                # 迁移热榜项目
                if data['hot_items']:
                    print("迁移热榜项目数据...")
                    await self.migrate_hot_items(session, data['hot_items'])
                
                # 验证迁移结果
                await self.verify_migration(session)
                
            except Exception as e:
                print(f"迁移过程中出现错误: {e}")
                await session.rollback()
                raise
        
        # 3. 输出迁移统计
        print("\n=== 迁移统计 ===")
        print(f"成功迁移:")
        print(f"  平台: {self.migration_stats['platforms']}")
        print(f"  分类: {self.migration_stats['categories']}")
        print(f"  热榜项目: {self.migration_stats['hot_items']}")
        
        if self.migration_stats['errors']:
            print(f"\n错误 ({len(self.migration_stats['errors'])})：")
            for error in self.migration_stats['errors'][:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(self.migration_stats['errors']) > 10:
                print(f"  ... 还有 {len(self.migration_stats['errors']) - 10} 个错误")
        
        print("\n迁移完成！")

async def main():
    """主函数"""
    # 查找 SQLite 数据库文件
    possible_paths = [
        "app.db",
        "momoyu.db",
        "../app.db",
        "../momoyu.db"
    ]
    
    sqlite_db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            sqlite_db_path = path
            break
    
    if not sqlite_db_path:
        print("未找到 SQLite 数据库文件")
        print("请确保以下文件之一存在:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    print(f"找到 SQLite 数据库: {sqlite_db_path}")
    
    # 执行迁移
    migrator = DatabaseMigrator(sqlite_db_path)
    await migrator.run_migration()
    
    # 关闭数据库连接
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())