#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟API服务器 - 用于测试前端功能
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if parsed_path.path == '/api/v1/hot/':
            # 解析查询参数
            query_params = parse_qs(parsed_path.query)
            size = int(query_params.get('size', [10])[0])  # 默认10条
            
            # 生成足够的模拟数据
            def generate_platform_data(platform_name, base_url, count):
                data = []
                titles = {
                    'NGA': ['客户端闪退问题解决方案', '游戏攻略分享', '技术讨论热帖', '社区活动通知', '新手指南', '装备推荐', '副本攻略', 'PVP技巧', '公会招募', '游戏资讯'],
                    '知乎': ['程序员职业发展', '人工智能前景', '投资理财建议', '教育改革讨论', '科技趋势分析', '创业经验分享', '心理健康话题', '社会现象观察', '历史文化探讨', '生活哲学思考'],
                    '微博': ['明星动态', '社会热点', '搞笑段子', '美食分享', '旅游攻略', '时尚潮流', '体育赛事', '影视剧评', '音乐推荐', '科技新闻'],
                    'B站': ['技术教程', '游戏解说', '美食制作', '音乐创作', '动画推荐', '学习方法', '生活vlog', '科普知识', '手工制作', '数码评测'],
                    '今日头条': ['时政新闻', '财经资讯', '科技动态', '娱乐八卦', '体育新闻', '健康养生', '教育资讯', '汽车资讯', '房产信息', '军事新闻'],
                    '虎扑': ['篮球讨论', '足球分析', '步行街话题', '数码产品', '汽车评测', '游戏推荐', '职场经验', '情感话题', '美食推荐', '旅游分享'],
                    'IT之家': ['Windows更新', 'iPhone新闻', '安卓系统', '硬件评测', '软件推荐', '网络安全', '人工智能', '云计算', '区块链', '物联网'],
                    '中关村在线': ['显卡评测', 'CPU性能', '笔记本推荐', '手机对比', '相机测试', '音响评价', '键盘鼠标', '显示器选择', '存储设备', '网络设备']
                }
                
                platform_titles = titles.get(platform_name, ['热门话题'] * 10)
                for i in range(count):
                    title_index = i % len(platform_titles)
                    data.append({
                        'title': f"{platform_titles[title_index]} {i+1}",
                        'url': base_url,
                        'platform_name': platform_name,
                        'hot_value': str(1000 - i * 10) if platform_name in ['NGA', '虎扑'] else f"{500 - i * 5}万",
                        'rank': i + 1
                    })
                return data
            
            # 计算每个平台的数据量（平均分配）
            platforms = [
                ('NGA', 'https://nga.178.com'),
                ('知乎', 'https://zhihu.com'),
                ('微博', 'https://weibo.com'),
                ('B站', 'https://bilibili.com'),
                ('今日头条', 'https://toutiao.com'),
                ('虎扑', 'https://hupu.com'),
                ('IT之家', 'https://ithome.com'),
                ('中关村在线', 'https://zol.com.cn')
            ]
            
            items_per_platform = max(1, size // len(platforms))
            remaining_items = size % len(platforms)
            
            all_items = []
            for i, (platform_name, base_url) in enumerate(platforms):
                count = items_per_platform + (1 if i < remaining_items else 0)
                platform_data = generate_platform_data(platform_name, base_url, count)
                all_items.extend(platform_data)
            
            # 确保不超过请求的数量
            all_items = all_items[:size]
            
            mock_data = {
                "success": True,
                "data": {
                    "items": all_items,
                    "total": len(all_items),
                    "page": 1,
                    "size": size
                },
                "message": "获取成功",
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            response = json.dumps(mock_data, ensure_ascii=False, indent=2)
            self.wfile.write(response.encode('utf-8'))
        else:
            # 404响应
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not Found"}')
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockAPIHandler)
    print(f"模拟API服务器启动在 http://localhost:{port}")
    print("API端点: http://localhost:8000/api/v1/hot/")
    print("按 Ctrl+C 停止服务器")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    run_server()