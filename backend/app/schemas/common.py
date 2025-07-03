from pydantic import BaseModel
from typing import Optional


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = 1
    size: int = 20
    
    class Config:
        from_attributes = True


class ResponseBase(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: Optional[str] = None
    
    class Config:
        from_attributes = True