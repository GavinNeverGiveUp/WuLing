from datetime import datetime
from fastapi import APIRouter, FastAPI
from typing import List, Optional
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException

from auth.auth_handler import get_current_user
from db.db_tools import get_db
from schema.models import FamilyCreate, FamilyResponse, ItemCreate, ItemResponse, ItemUpdate, UserCreate, UserLogin, UserResponse
from utils.func_utils import get_default_family, get_password_hash, get_user_by_username, get_user_families, get_user_id_by_username, verify_password

item_app = APIRouter(prefix="/item", tags=["物品管理"])

# 物品管理相关接口（在主应用中）
@item_app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, current_user: str = Depends(get_current_user)):
    # 获取用户ID
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 确定家庭ID
    family_id = item.family_id
    if not family_id:
        # 使用默认家庭
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT default_family_id FROM users WHERE id=?",
                (user_id,)
            )
            default_family = cursor.fetchone()
            if not default_family or not default_family[0]:
                # 如果没有默认家庭，使用第一个家庭
                families = get_user_families(user_id)
                if not families:
                    raise HTTPException(status_code=400, detail="用户没有家庭")
                family_id = families[0]["id"]
            else:
                family_id = default_family[0]
    else:
        # 验证用户是否是指定家庭的成员
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role FROM user_families WHERE user_id=? AND family_id=?",
                (user_id, family_id)
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="您不是该家庭的成员")
    
    item_id = str(uuid4())
    created_at = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (id, name, description, location, family_id, added_by, created_at, expiration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (item_id, item.name, item.description, item.location, family_id, user_id, created_at, item.expiration_date)
        )
        conn.commit()
    
    return {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "location": item.location,
        "family_id": family_id,
        "added_by": user_id,
        "created_at": created_at,
        "expiration_date": item.expiration_date
    }

@item_app.get("/items", response_model=List[ItemResponse])
def get_items(current_user: str = Depends(get_current_user)):
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    families = get_user_families(user_id)
    if not families:
        raise HTTPException(status_code=400, detail="用户没有家庭")
    
    family_ids = [f["id"] for f in families]
    placeholders = ','.join(['?' for _ in family_ids])
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = f"SELECT id, name, description, location, family_id, added_by, created_at, expiration_date FROM items WHERE family_id IN ({placeholders})"
        cursor.execute(query, family_ids)
        rows = cursor.fetchall()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "location": row[3],
            "family_id": row[4],
            "added_by": row[5],
            "created_at": row[6],
            "expiration_date": row[7]
        }
        for row in rows
    ]

@item_app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: str, item_update: ItemUpdate, current_user: str = Depends(get_current_user)):
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查物品是否存在且属于当前用户
        cursor.execute(
            "SELECT family_id FROM items WHERE id=? AND added_by=?",
            (item_id, user_id)
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="物品不存在或无权修改")
        
        # 更新物品信息
        update_fields = []
        update_values = []
        
        if item_update.name is not None:
            update_fields.append("name = ?")
            update_values.append(item_update.name)
        if item_update.description is not None:
            update_fields.append("description = ?")
            update_values.append(item_update.description)
        if item_update.location is not None:
            update_fields.append("location = ?")
            update_values.append(item_update.location)
        if item_update.expiration_date is not None:
            update_fields.append("expiration_date = ?")
            update_values.append(item_update.expiration_date)
        
        if update_fields:
            update_query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(update_query, update_values + [item_id])
        
        # 获取更新后的数据
        cursor.execute("SELECT id, name, description, location, family_id, added_by, created_at, expiration_date FROM items WHERE id=?", (item_id,))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "location": row[3],
        "family_id": row[4],
        "added_by": row[5],
        "created_at": row[6],
        "expiration_date": row[7]
    }

@item_app.delete("/items/{item_id}")
def delete_item(item_id: str, current_user: str = Depends(get_current_user)):
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items WHERE id=? AND added_by=?", (item_id, user_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="物品不存在或无权删除")
    
    return {"message": "删除成功"}