from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from datetime import datetime

# 基础用户模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")

# 用户创建模型
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="用户密码")

# 用户更新模型
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

# 数据库中的用户模型
class UserInDBBase(UserBase):
    id: uuid.UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 返回给客户端的用户模型
class User(UserInDBBase):
    pass

# 登录模型
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")

# Token模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None