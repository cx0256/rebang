import asyncio
from app.crawlers.crawler_manager import crawler_manager
from app.core.database import get_async_session
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem
from datetime import datetime
from sqlalchemy import select

async def create_smzdm():
    async for db in get_async_session():
        try:
            # 创建平台
            platform = await crawler_manager._get_or_create_platform(db, 'smzdm')
            print(f"平台: {platform.display_name}")
            
            # 创建分类
            category = await crawler_manager._get_or_create_category(db, platform.id, 'hot')
            print(f"分类: {category.display_name}")
            
            # 检查是否已有数据
            stmt = select(HotItem).where(HotItem.category_id == category.id)
            result = await db.execute(stmt)
            existing_items = result.scalars().all()
            
            if not existing_items:
                # 添加测试数据
                test_items = [
                    HotItem(
                        title='iPhone 15 Pro Max 256GB 天然钛色 好价推荐',
                        url='https://www.smzdm.com/p/123456/',
                        rank=1,
                        hot_value='9999',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='小米14 Ultra 16GB+1TB 黑色 限时优惠',
                        url='https://www.smzdm.com/p/123457/',
                        rank=2,
                        hot_value='8888',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='华为Mate 60 Pro 12GB+512GB 雅川青 新品上市',
                        url='https://www.smzdm.com/p/123458/',
                        rank=3,
                        hot_value='7777',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='戴森V15 Detect无线吸尘器 官方直降',
                        url='https://www.smzdm.com/p/123459/',
                        rank=4,
                        hot_value='6666',
                        category_id=category.id,
                        publish_time=datetime.now()
                    ),
                    HotItem(
                        title='任天堂Switch OLED 马力欧红色限定版',
                        url='https://www.smzdm.com/p/123460/',
                        rank=5,
                        hot_value='5555',
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
            print("创建完成！")
            
        except Exception as e:
            await db.rollback()
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == '__main__':
    asyncio.run(create_smzdm())