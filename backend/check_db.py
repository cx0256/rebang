import sqlite3
import os

db_path = 'app.db'
print(f'检查数据库文件: {db_path}')
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'数据库中的表: {[t[0] for t in tables]}')
        
        if 'hot_items' in [t[0] for t in tables]:
            cursor.execute('SELECT platform_name, category_name, COUNT(*) as count, MAX(crawled_at) as last_crawl FROM hot_items GROUP BY platform_name, category_name ORDER BY platform_name, category_name')
            results = cursor.fetchall()
            
            print('\nPlatform | Category | Count | Last Crawl')
            print('-' * 60)
            for r in results:
                print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
                
            # 查询NGA数据
            cursor.execute("SELECT title, rank_position, crawled_at FROM hot_items WHERE platform_name='NGA' AND category_name='杂谈' ORDER BY rank_position LIMIT 10")
            nga_results = cursor.fetchall()
            
            print('\nNGA杂谈前10条数据:')
            print('-' * 60)
            for r in nga_results:
                print(f'排名: {r[1]}, 标题: {r[0][:50]}..., 时间: {r[2]}')
        else:
            print('hot_items表不存在')
            
    except Exception as e:
        print(f'查询失败: {e}')
    finally:
        conn.close()
else:
    print('数据库文件不存在')