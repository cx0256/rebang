#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import json

async def test_nga_login():
    """测试NGA登录状态"""
    with open('nga_cookies.json', 'r', encoding='utf-8') as f:
        cookies_dict = json.load(f)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://bbs.nga.cn/', cookies=cookies_dict, headers=headers) as response:
            content = await response.text()
            print(f'Status: {response.status}')
            print(f'Content length: {len(content)}')
            
            # 检查登录相关的关键词
            keywords = ['退出', 'logout', '登录', 'login', '用户名', 'username', 'ngaPassportUid']
            found_keywords = []
            for keyword in keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            print(f'Found keywords: {found_keywords}')
            
            # 检查是否有用户信息
            if 'ngaPassportUid' in content:
                print('Found ngaPassportUid in page content')
            
            # 保存部分内容用于分析
            with open('nga_page_content.txt', 'w', encoding='utf-8') as f:
                f.write(content[:5000])  # 只保存前5000字符
            print('Page content saved to nga_page_content.txt')

if __name__ == '__main__':
    asyncio.run(test_nga_login())