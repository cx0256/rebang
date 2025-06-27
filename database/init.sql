-- 热榜数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 热榜平台表
CREATE TABLE platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    base_url VARCHAR(255),
    icon_url VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 热榜分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES platforms(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, name)
);

-- 热榜条目表
CREATE TABLE hot_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    description TEXT,
    author VARCHAR(100),
    score INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    rank_position INTEGER,
    source_id VARCHAR(100), -- 原平台的ID
    tags TEXT[], -- 标签数组
    published_at TIMESTAMP WITH TIME ZONE,
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 爬取任务表
CREATE TABLE crawl_tasks (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    items_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户表（用于管理后台）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_hot_items_category_id ON hot_items(category_id);
CREATE INDEX idx_hot_items_crawled_at ON hot_items(crawled_at);
CREATE INDEX idx_hot_items_rank_position ON hot_items(rank_position);
CREATE INDEX idx_hot_items_published_at ON hot_items(published_at);
CREATE INDEX idx_crawl_tasks_category_id ON crawl_tasks(category_id);
CREATE INDEX idx_crawl_tasks_status ON crawl_tasks(status);

-- 插入初始平台数据
INSERT INTO platforms (name, display_name, base_url, description) VALUES
('zhihu', '知乎', 'https://www.zhihu.com', '知识分享社区'),
('weibo', '微博', 'https://weibo.com', '社交媒体平台'),
('douban', '豆瓣', 'https://www.douban.com', '文艺生活社区'),
('bilibili', 'B站', 'https://www.bilibili.com', '视频分享平台'),
('github', 'GitHub', 'https://github.com', '代码托管平台'),
('v2ex', 'V2EX', 'https://www.v2ex.com', '技术社区'),
('juejin', '掘金', 'https://juejin.cn', '技术分享社区'),
('baidu', '百度', 'https://www.baidu.com', '搜索引擎');

-- 插入初始分类数据
INSERT INTO categories (platform_id, name, display_name, api_endpoint) VALUES
(1, 'hot', '知乎热榜', '/api/v1/zhihu/hot'),
(2, 'hot', '微博热搜', '/api/v1/weibo/hot'),
(3, 'movie', '豆瓣电影', '/api/v1/douban/movie'),
(3, 'book', '豆瓣读书', '/api/v1/douban/book'),
(4, 'popular', 'B站热门', '/api/v1/bilibili/popular'),
(5, 'trending', 'GitHub趋势', '/api/v1/github/trending'),
(6, 'hot', 'V2EX热议', '/api/v1/v2ex/hot'),
(7, 'hot', '掘金热榜', '/api/v1/juejin/hot'),
(8, 'hot', '百度热搜', '/api/v1/baidu/hot');

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_platforms_updated_at BEFORE UPDATE ON platforms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hot_items_updated_at BEFORE UPDATE ON hot_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();