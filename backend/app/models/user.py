from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    last_login = Column(DateTime(timezone=True), comment="最后登录时间")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_safe_dict(self):
        """转换为安全字典（不包含敏感信息）"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def to_token_dict(self):
        """转换为Token载荷字典"""
        return {
            "user_id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin
        }
    
    @classmethod
    def create_from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False)
        )
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = func.now()
    
    def activate(self):
        """激活用户"""
        self.is_active = True
    
    def deactivate(self):
        """停用用户"""
        self.is_active = False
    
    def make_admin(self):
        """设为管理员"""
        self.is_admin = True
    
    def remove_admin(self):
        """取消管理员"""
        self.is_admin = False
    
    def check_password(self, password: str) -> bool:
        """检查密码（需要配合密码哈希工具使用）"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, self.password_hash)
    
    def set_password(self, password: str):
        """设置密码（需要配合密码哈希工具使用）"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.password_hash = pwd_context.hash(password)