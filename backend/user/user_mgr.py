
# 用户和家庭管理子应用
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, FastAPI, HTTPException

from auth.auth_handler import create_access_token, get_current_user
from db.db_tools import get_db
from schema.models import FamilyCreate, FamilyResponse, MessageResponse, Token, UserCreate, UserLogin, UserResponse
from utils.func_utils import get_password_hash, get_user_by_username, get_user_families, get_user_id_by_username, verify_password


user_app = APIRouter(prefix="/user", tags=["用户和家庭管理"])

@user_app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    time_now = datetime.now()
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user_id = str(uuid4())
    password_hash = get_password_hash(user.password)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (id, username, email, phone, password_hash, create_time) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user.username, user.email, user.phone, password_hash, str(time_now))
        )
        conn.commit()
    
    return {"id": user_id, "username": user.username, "email": user.email, "phone": user.phone}

@user_app.post("/login", response_model=Token)
def login_user(credentials: UserLogin):
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 创建token
    access_token = create_access_token(
        data={"sub": user["username"]},
    )
    return {"access_token": access_token, "token_type": "bearer"}

@user_app.get("/me", response_model=UserResponse)
def read_users_me(current_user: str = Depends(get_current_user)):
    # 根据当前用户名获取用户信息
    user_info = get_user_by_username(current_user)
    if not user_info:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"id": user_info["id"], "username": user_info["username"], "email": user_info["email"], "phone": user_info["phone"]}



@user_app.post("/families", response_model=FamilyResponse)
def create_family(family: FamilyCreate, current_user: str = Depends(get_current_user)):
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    family_id = str(uuid4())
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO families (id, name) VALUES (?, ?)",
            (family_id, family.name)
        )
        
        # 自动将创建者加入家庭
        cursor.execute(
            "INSERT INTO user_families (user_id, family_id, role) VALUES (?, ?, ?)",
            (user_id, family_id, "owner")
        )
        conn.commit()
    
    return {"id": family_id, "name": family.name}

@user_app.get("/families", response_model=List[FamilyResponse])
def get_user_families_endpoint(current_user: str = Depends(get_current_user)):

    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    families = get_user_families(user_id)
    return families

