import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app.core.database import get_async_session
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem
from datetime import datetime

async def create_smzdm_platform():
    async for db in get_async_session():
        try:
            # 检查平台是否已存在
            from sqlalchemy import select
            stmt = select(Platform).where(Platform.name == 'smzdm')
            result = await db.execute(stmt)
            platform = result.scalar_one_or_none()
            
            if platform:
                print(f"平台已存在: {platform.display_name}")
            else:
                # 创建平台
                platform = Platform(
                    name='smzdm',
                    code='smzdm',
                    display_name='什么值得买',
                    description='什么值得买热榜',
                    base_url='https://www.smzdm.com',
                    is_active=True,
                    sort_order=9
                )
                db.add(platform)
                await db.flush()  # 获取ID
                print(f"创建平台: {platform.display_name}")
            
            # 检查分类是否已存在
            stmt = select(Category).where(
                Category.platform_id == platform.id,
                Category.name == 'hot'
            )
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()
            
            if category:
                print(f"分类已存在: {category.display_name}")
            else:
                # 创建分类
                category = Category(
                    name='hot',
                    display_name='热榜',
                    description='什么值得买热榜',
                    platform_id=platform.id,
                    is_active=True,
                    sort_order=1
                )
                db.add(category)
                await db.flush()
                print(f"创建分类: {category.display_name}")
            
            # 添加一些测试数据
            stmt = select(HotItem).where(HotItem.category_id == category.id)
            result = await db.execute(stmt)
            existing_items = result.scalars().all()
            
            if not existing_items:
                test_items = [
                    HotItem(
                        title='iPhone 15 Pro Max 256GB 天然钛色',
                        url='https://www.smzdm.com/p/123456/',
                        rank=1,
                        hot_value='9999',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='小米14 Ultra 16GB+1TB 黑色',
                        url='https://www.smzdm.com/p/123457/',
                        rank=2,
                        hot_value='8888',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='华为Mate 60 Pro 12GB+512GB 雅川青',
                        url='https://www.smzdm.com/p/123458/',
                        rank=3,
                        hot_value='7777',
                        category_id=category.id,
                        publish_time=datetime.now()
                    )
                ]
                
                for item in test_items:
                    db.add(item)
                
                print(f"添加了 {len(test_items)} 条测试数据")
            else:
                print(f"已存在 {len(existing_items)} 条数据")
            
            await db.commit()
            print("操作完成！")
            
        except Exception as e:
            await db.rollback()
            print(f"错误: {e}")
            raise
        finally:
            await db.close()
            break

if __name__ == '__main__':
    asyncio.run(create_smzdm_platform())