from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class HotItemBase(BaseModel):
    """热榜条目基础模型"""
    title: str
    url: str
    rank: Optional[int] = None
    heat_score: Optional[float] = None
    description: Optional[str] = None
    author: Optional[str] = None
    comment_count: Optional[int] = None
    like_count: Optional[int] = None
    share_count: Optional[int] = None


class HotItemResponse(HotItemBase):
    """热榜条目响应模型"""
    id: int
    platform_name: str
    category_name: str
    crawl_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HotItemListResponse(BaseModel):
    """热榜条目列表响应模型"""
    items: List[HotItemResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True