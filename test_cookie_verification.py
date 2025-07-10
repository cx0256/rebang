#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import json
import re

async def verify_nga_cookies():
    """验证NGA Cookie有效性"""
    print("\n✅ 验证Cookie有效性")
    
    # 加载cookies
    try:
        with open('nga_cookies.json', 'r', encoding='utf-8') as f:
            cookies = json.load(f)
    except Exception as e:
        print(f"❌ 未找到保存的Cookie: {e}")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试访问NGA首页
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with session.get(
                'https://bbs.nga.cn/',
                cookies=cookies,
                headers=headers,
                timeout=10
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 检查登录状态 - 更准确的方法
                    # 检查是否有用户ID和用户名信息
                    if '__CURRENT_UID' in content and '__CURRENT_UNAME' in content:
                        # 提取用户ID
                        uid_match = re.search(r'__CURRENT_UID = parseInt\(\'(\d+)\',10\)', content)
                        uname_match = re.search(r'__CURRENT_UNAME = \'([^\']*)\',', content)
                        
                        if uid_match and uname_match and uid_match.group(1) != '0':
                            uid = uid_match.group(1)
                            uname = uname_match.group(1)
                            print(f"✅ Cookie验证成功 - 已登录状态")
                            print(f"   用户ID: {uid}")
                            print(f"   用户名: {uname}")
                            return True
                        else:
                            print("⚠️ Cookie可能已失效 - 用户ID为0或未找到用户信息")
                            return False
                    else:
                        print("⚠️ Cookie可能已失效 - 未检测到登录状态")
                        return False
                else:
                    print(f"❌ 访问失败 - HTTP {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(verify_nga_cookies())