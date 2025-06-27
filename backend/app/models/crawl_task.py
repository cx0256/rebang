from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class CrawlTask(Base):
    """爬取任务模型"""
    
    __tablename__ = "crawl_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属分类ID")
    status = Column(String(20), default=TaskStatus.PENDING.value, index=True, comment="任务状态")
    started_at = Column(DateTime(timezone=True), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    items_count = Column(Integer, default=0, comment="爬取条目数量")
    error_message = Column(Text, comment="错误信息")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    category = relationship("Category", back_populates="crawl_tasks")
    
    def __repr__(self):
        return f"<CrawlTask(id={self.id}, category_id={self.category_id}, status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "items_count": self.items_count,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "category": self.category.to_simple_dict() if self.category else None,
            "duration": self.get_duration()
        }
    
    def to_simple_dict(self):
        """转换为简单字典（不包含关联数据）"""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "items_count": self.items_count,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "duration": self.get_duration()
        }
    
    def get_duration(self):
        """获取任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (func.now() - self.started_at).total_seconds()
        return None
    
    def is_running(self):
        """检查任务是否正在运行"""
        return self.status == TaskStatus.RUNNING.value
    
    def is_completed(self):
        """检查任务是否已完成"""
        return self.status == TaskStatus.COMPLETED.value
    
    def is_failed(self):
        """检查任务是否失败"""
        return self.status == TaskStatus.FAILED.value
    
    def mark_as_running(self):
        """标记为运行中"""
        self.status = TaskStatus.RUNNING.value
        self.started_at = func.now()
        self.error_message = None
    
    def mark_as_completed(self, items_count: int = 0):
        """标记为已完成"""
        self.status = TaskStatus.COMPLETED.value
        self.completed_at = func.now()
        self.items_count = items_count
        self.error_message = None
    
    def mark_as_failed(self, error_message: str):
        """标记为失败"""
        self.status = TaskStatus.FAILED.value
        self.completed_at = func.now()
        self.error_message = error_message
    
    def mark_as_cancelled(self):
        """标记为已取消"""
        self.status = TaskStatus.CANCELLED.value
        self.completed_at = func.now()
    
    @classmethod
    def create_from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            category_id=data.get("category_id"),
            status=data.get("status", TaskStatus.PENDING.value)
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