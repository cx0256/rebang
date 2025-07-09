from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class HotItem(Base):
    """热榜条目模型"""
    
    __tablename__ = "hot_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属分类ID")
    title = Column(String(500), nullable=False, comment="标题")
    url = Column(String(2000), comment="链接地址")
    description = Column(Text, comment="描述")
    author = Column(String(100), comment="作者")
    score = Column(Integer, default=0, comment="热度分数")
    comment_count = Column(Integer, default=0, comment="评论数")
    rank_position = Column(Integer, index=True, comment="排名位置")
    source_id = Column(String(100), comment="原平台ID")
    tags = Column(JSON, comment="标签数组")
    
    # 时间戳
    published_at = Column(DateTime(timezone=True), comment="发布时间")
    crawled_at = Column(DateTime(timezone=True), server_default=func.now(), comment="爬取时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    category = relationship("Category", back_populates="hot_items")
    
    def __repr__(self):
        return f"<HotItem(id={self.id}, title='{self.title[:50]}...', rank={self.rank_position})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "category_id": self.category_id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "author": self.author,
            "score": self.score,
            "comment_count": self.comment_count,
            "rank_position": self.rank_position,
            "source_id": self.source_id,
            "tags": self.tags or [],
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "category": self.category.to_simple_dict() if self.category else None
        }
    
    def to_simple_dict(self):
        """转换为简单字典（不包含关联数据）"""
        return {
            "id": str(self.id),
            "category_id": self.category_id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "author": self.author,
            "score": self.score,
            "comment_count": self.comment_count,
            "rank_position": self.rank_position,
            "source_id": self.source_id,
            "tags": self.tags or [],
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_list_dict(self):
        """转换为列表显示字典（精简版）"""
        return {
            "id": str(self.id),
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "score": self.score,
            "comment_count": self.comment_count,
            "rank_position": self.rank_position,
            "tags": self.tags or [],
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
    
    @classmethod
    def create_from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            category_id=data.get("category_id"),
            title=data.get("title"),
            url=data.get("url"),
            description=data.get("description"),
            author=data.get("author"),
            score=data.get("score", 0),
            comment_count=data.get("comment_count", 0),
            rank_position=data.get("rank_position"),
            source_id=data.get("source_id"),
            tags=data.get("tags", []),
            published_at=data.get("published_at")
        )
    
    @property
    def platform_name(self):
        """获取平台名称"""
        if self.category and self.category.platform:
            return self.category.platform.name
        return None
    
    @property
    def category_name(self):
        """获取分类名称"""
        if self.category:
            return self.category.name
        return None