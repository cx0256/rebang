from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Platform(Base):
    """热榜平台模型"""
    
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True, comment="平台标识名")
    display_name = Column(String(100), nullable=False, comment="平台显示名称")
    base_url = Column(String(255), comment="平台基础URL")
    icon_url = Column(String(255), comment="平台图标URL")
    description = Column(Text, comment="平台描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    categories = relationship("Category", back_populates="platform", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Platform(id={self.id}, name='{self.name}', display_name='{self.display_name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "base_url": self.base_url,
            "icon_url": self.icon_url,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "categories_count": len(self.categories) if self.categories else 0
        }
    
    @classmethod
    def create_from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            name=data.get("name"),
            display_name=data.get("display_name"),
            base_url=data.get("base_url"),
            icon_url=data.get("icon_url"),
            description=data.get("description"),
            is_active=data.get("is_active", True)
        )