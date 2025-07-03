from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Category(Base):
    """热榜分类模型"""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False, comment="所属平台ID")
    name = Column(String(50), nullable=False, comment="分类标识名")
    display_name = Column(String(100), nullable=False, comment="分类显示名称")
    api_endpoint = Column(String(255), comment="API端点")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 唯一约束：同一平台下分类名不能重复
    __table_args__ = (
        UniqueConstraint('platform_id', 'name', name='uq_platform_category'),
    )
    
    # 关系
    platform = relationship("Platform", back_populates="categories")
    hot_items = relationship("HotItem", back_populates="category", cascade="all, delete-orphan")
    crawl_tasks = relationship("CrawlTask", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', platform_id={self.platform_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "platform_id": self.platform_id,
            "name": self.name,
            "display_name": self.display_name,
            "api_endpoint": self.api_endpoint,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "platform": self.platform.to_dict() if self.platform else None,
            "hot_items_count": len(self.hot_items) if self.hot_items else 0
        }
    
    def to_simple_dict(self):
        """转换为简单字典（不包含关联数据）"""
        return {
            "id": self.id,
            "platform_id": self.platform_id,
            "name": self.name,
            "display_name": self.display_name,
            "api_endpoint": self.api_endpoint,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            platform_id=data.get("platform_id"),
            name=data.get("name"),
            display_name=data.get("display_name"),
            api_endpoint=data.get("api_endpoint"),
            is_active=data.get("is_active", True)
        )