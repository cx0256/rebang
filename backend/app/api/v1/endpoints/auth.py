from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.schemas.user import User, UserCreate, Token
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_user_by_email,
    get_password_hash
)
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 检查邮箱是否已存在
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {
        "code": 0,
        "data": {
            "access_token": access_token, 
            "token_type": "bearer"
        },
        "message": "success"
    }

@router.post("/logout")
async def logout():
    # 对于JWT token，logout通常在客户端处理
    # 这里返回成功响应即可
    return {"message": "Successfully logged out"}

@router.get("/me")
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    # 返回前端期望的用户信息格式
    user_data = {
        "userId": str(current_user.id),
        "username": current_user.username,
        "realName": current_user.username,  # 使用username作为realName
        "avatar": "https://api.dicebear.com/7.x/miniavs/svg?seed=" + current_user.username,
        "roles": ["admin"] if current_user.email == "admin@example.com" else ["user"],
        "desc": "Administrator" if current_user.email == "admin@example.com" else "User",
        "homePath": "/dashboard",
        "token": ""  # token由前端管理
    }
    return {
        "code": 0,
        "data": user_data,
        "message": "success"
    }

@router.get("/codes")
async def get_access_codes(current_user: UserModel = Depends(get_current_active_user)):
    # 返回用户权限代码
    # 这里可以根据用户角色返回不同的权限代码
    if current_user.email == "admin@example.com":
        codes = ["AC_100100", "AC_100110", "AC_100120", "AC_100010"]
    else:
        codes = ["AC_100010"]  # 普通用户权限
    
    return {
        "code": 0,
        "data": codes,
        "message": "success"
    }