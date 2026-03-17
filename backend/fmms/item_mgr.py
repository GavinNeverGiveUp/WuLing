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
async def create_item(item: ItemCreate, current_user: str = Depends(get_current_user)):
    # 获取用户ID
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 确定家庭ID
    family_id = item.family_id
    if not family_id:
        # 使用默认家庭
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (user_id,)
                )
                default_family = await cursor.fetchone()
                if not default_family or not default_family['default_family_id']:
                    # 如果没有默认家庭，使用第一个家庭
                    families = await get_user_families(user_id)
                    if not families:
                        raise HTTPException(status_code=400, detail="用户没有家庭")
                    family_id = families[0]["id"]
                else:
                    family_id = default_family['default_family_id']
    else:
        # 验证用户是否是指定家庭的成员
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                    (user_id, family_id)
                )
                if not await cursor.fetchone():
                    raise HTTPException(status_code=403, detail="您不是该家庭的成员")
    
    item_id = str(uuid4())
    created_at = datetime.now().isoformat()
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO items (id, name, description, location, family_id, added_by, created_at, expiration_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (item_id, item.name, item.description, item.location, family_id, user_id, created_at, item.expiration_date)
            )
            await conn.commit()
    
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
async def get_items(current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    families = await get_user_families(user_id)
    if not families:
        raise HTTPException(status_code=400, detail="用户没有家庭")
    
    family_ids = [f["id"] for f in families]
    placeholders = ','.join(['%s' for _ in family_ids])
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            query = f"SELECT id, name, description, location, family_id, added_by, created_at, expiration_date FROM items WHERE family_id IN ({placeholders})"
            await cursor.execute(query, family_ids)
            rows = await cursor.fetchall()
    
    return [
        {
            "id": row['id'],
            "name": row['name'],
            "description": row['description'],
            "location": row['location'],
            "family_id": row['family_id'],
            "added_by": row['added_by'],
            "created_at": row['created_at'].isoformat() if row['created_at'] else None,
            "expiration_date": row['expiration_date'].isoformat() if row['expiration_date'] else None
        }
        for row in rows
    ]

@item_app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_update: ItemUpdate, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            # 检查物品是否存在
            await cursor.execute(
                "SELECT family_id, added_by FROM items WHERE id=%s",
                (item_id,)
            )
            item_info = await cursor.fetchone()
            if not item_info:
                raise HTTPException(status_code=404, detail="物品不存在")
            
            family_id = item_info['family_id']
            added_by = item_info['added_by']
            
            # 检查当前用户是否是物品的拥有者
            if user_id == added_by:
                # 是拥有者，允许修改
                pass
            else:
                # 不是拥有者，检查是否是家庭owner
                await cursor.execute(
                    "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                    (user_id, family_id)
                )
                role_info = await cursor.fetchone()
                if not role_info or role_info['role'] != 'owner':
                    raise HTTPException(status_code=403, detail="无权修改此物品")
            
            # 更新物品信息
            update_fields = []
            update_values = []
            
            if item_update.name is not None:
                update_fields.append("name = %s")
                update_values.append(item_update.name)
            if item_update.description is not None:
                update_fields.append("description = %s")
                update_values.append(item_update.description)
            if item_update.location is not None:
                update_fields.append("location = %s")
                update_values.append(item_update.location)
            if item_update.expiration_date is not None:
                update_fields.append("expiration_date = %s")
                update_values.append(item_update.expiration_date)
            
            if update_fields:
                update_query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = %s"
                await cursor.execute(update_query, update_values + [item_id])
                await conn.commit()
            
            # 获取更新后的数据
            await cursor.execute("SELECT id, name, description, location, family_id, added_by, created_at, expiration_date FROM items WHERE id=%s", (item_id,))
            row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    return {
        "id": row['id'],
        "name": row['name'],
        "description": row['description'],
        "location": row['location'],
        "family_id": row['family_id'],
        "added_by": row['added_by'],
        "created_at": row['created_at'].isoformat() if row['created_at'] else None,
        "expiration_date": row['expiration_date'].isoformat() if row['expiration_date'] else None
    }

@item_app.delete("/items/{item_id}")
async def delete_item(item_id: str, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            # 检查物品是否存在
            await cursor.execute(
                "SELECT family_id, added_by FROM items WHERE id=%s",
                (item_id,)
            )
            item_info = await cursor.fetchone()
            if not item_info:
                raise HTTPException(status_code=404, detail="物品不存在")
            
            family_id = item_info['family_id']
            added_by = item_info['added_by']
            
            # 检查当前用户是否是物品的拥有者
            if user_id == added_by:
                # 是拥有者，允许删除
                pass
            else:
                # 不是拥有者，检查是否是家庭owner
                await cursor.execute(
                    "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                    (user_id, family_id)
                )
                role_info = await cursor.fetchone()
                if not role_info or role_info['role'] != 'owner':
                    raise HTTPException(status_code=403, detail="无权删除此物品")
            
            # 执行删除操作
            await cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
            await conn.commit()
    
    return {"message": "删除成功"}
