# 用户和家庭管理子应用
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, FastAPI, HTTPException

from auth.auth_handler import create_access_token, get_current_user
from db.db_tools import get_db
from schema.models import ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeyListItem, FamilyCreate, FamilyResponse, MessageResponse, Token, UserCreate, UserLogin, UserResponse, FamilyInvitationCreate, FamilyInvitationResponse, FamilyInvitationAction, RemoveMemberRequest, UpdateMemberRoleRequest
from user.USER_MGR_CTRL import create_api_key_for_user, list_api_keys_by_user, revoke_api_key_for_user
from utils.func_utils import get_password_hash, get_user_by_username, get_user_families, get_user_id_by_username, verify_password


user_app = APIRouter(prefix="/user", tags=["用户和家庭管理"])

@user_app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    time_now = datetime.now()
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user_id = str(uuid4())
    password_hash = get_password_hash(user.password)
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (id, username, email, phone, password_hash, create_time) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, user.username, user.email, user.phone, password_hash, str(time_now))
            )
            await conn.commit()
    
    return {"id": user_id, "username": user.username, "email": user.email, "phone": user.phone}

@user_app.post("/login", response_model=Token)
async def login_user(credentials: UserLogin):
    user = await get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 创建token
    access_token = create_access_token(
        data={"sub": user["username"]},
    )
    return {"access_token": access_token, "token_type": "bearer"}

@user_app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: str = Depends(get_current_user)):
    # 根据当前用户名获取用户信息
    user_info = await get_user_by_username(current_user)
    if not user_info:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"id": user_info["id"], "username": user_info["username"], "email": user_info["email"], "phone": user_info["phone"]}



@user_app.post("/families", response_model=FamilyResponse)
async def create_family(family: FamilyCreate, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    family_id = str(uuid4())
    default_flag = False
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO families (id, name) VALUES (%s, %s)",
                (family_id, family.name)
            )
            
            # 自动将创建者加入家庭
            await cursor.execute(
                "INSERT INTO user_families (user_id, family_id, role) VALUES (%s, %s, %s)",
                (user_id, family_id, "owner")
            )
            
            # 检查用户是否已有默认家庭，如果没有则设置为默认家庭
            await cursor.execute(
                "SELECT default_family_id FROM users WHERE id=%s",
                (user_id,)
            )
            result = await cursor.fetchone()
            if not result or not result['default_family_id']:
                await cursor.execute(
                    "UPDATE users SET default_family_id=%s WHERE id=%s",
                    (family_id, user_id)
                )
                default_flag = True
            
            await conn.commit()
    
    return {"id": family_id, "name": family.name, "role": "owner", "is_default": default_flag}

@user_app.get("/families", response_model=List[FamilyResponse])
async def get_user_families_endpoint(current_user: str = Depends(get_current_user)):

    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    families = await get_user_families(user_id)
    return families

@user_app.delete("/families/{family_id}")
async def delete_family(family_id: str, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, name FROM families WHERE id=%s",
                (family_id,)
            )
            family = await cursor.fetchone()
            if not family:
                raise HTTPException(status_code=404, detail="家庭不存在")

            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (user_id, family_id)
            )
            membership = await cursor.fetchone()
            if not membership or membership['role'] != 'owner':
                raise HTTPException(status_code=403, detail="只有家庭管理员才能删除家庭")

            await cursor.execute(
                "SELECT user_id FROM user_families WHERE family_id=%s",
                (family_id,)
            )
            member_rows = await cursor.fetchall()
            member_ids = [row['user_id'] for row in member_rows]

            await cursor.execute(
                "DELETE FROM items WHERE family_id=%s",
                (family_id,)
            )
            await cursor.execute(
                "DELETE FROM family_invitations WHERE family_id=%s",
                (family_id,)
            )
            await cursor.execute(
                "DELETE FROM user_families WHERE family_id=%s",
                (family_id,)
            )
            await cursor.execute(
                "DELETE FROM families WHERE id=%s",
                (family_id,)
            )

            for member_id in member_ids:
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (member_id,)
                )
                default_family = await cursor.fetchone()
                if not default_family or default_family['default_family_id'] != family_id:
                    continue

                await cursor.execute(
                    """
                    SELECT family_id
                    FROM user_families
                    WHERE user_id=%s
                    ORDER BY family_id ASC
                    LIMIT 1
                    """,
                    (member_id,)
                )
                next_family = await cursor.fetchone()

                await cursor.execute(
                    "UPDATE users SET default_family_id=%s WHERE id=%s",
                    (next_family['family_id'] if next_family else None, member_id)
                )

            await conn.commit()

    return {"message": f"Family {family['name']} deleted"}


@user_app.post("/families/invitations", response_model=FamilyInvitationResponse)
async def send_family_invitation(invitation: FamilyInvitationCreate, current_user: str = Depends(get_current_user)):
    inviter_id = await get_user_id_by_username(current_user)
    if not inviter_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查被邀请用户是否存在
    invitee = await get_user_by_username(invitation.invitee_username)
    if not invitee:
        raise HTTPException(status_code=404, detail="被邀请用户不存在")
    
    # 检查邀请者是否是家庭的成员
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (inviter_id, invitation.family_id)
            )
            if not await cursor.fetchone():
                raise HTTPException(status_code=403, detail="您不是该家庭的成员")
    
    # 创建邀请
    invitation_id = str(uuid4())
    created_at = datetime.now().isoformat()
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO family_invitations (id, family_id, inviter_id, invitee_username, status, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (invitation_id, invitation.family_id, inviter_id, invitation.invitee_username, "pending", created_at)
            )
            await conn.commit()
    
    return {
        "id": invitation_id,
        "family_id": invitation.family_id,
        "inviter_id": inviter_id,
        "invitee_username": invitation.invitee_username,
        "status": "pending",
        "created_at": created_at
    }

@user_app.get("/families/invitations", response_model=List[FamilyInvitationResponse])
async def get_pending_invitations(current_user: str = Depends(get_current_user)):
    username = current_user
    
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, family_id, inviter_id, invitee_username, status, created_at FROM family_invitations WHERE invitee_username=%s AND status=%s",
                (username, "pending")
            )
            rows = await cursor.fetchall()
    
    return [
        {
            "id": row['id'],
            "family_id": row['family_id'],
            "inviter_id": row['inviter_id'],
            "invitee_username": row['invitee_username'],
            "status": row['status'],
            "created_at": str(str(row['created_at']))
        }
        for row in rows
    ]

@user_app.post("/families/invitations/action")
async def handle_invitation_action(action: FamilyInvitationAction, current_user: str = Depends(get_current_user)):
    username = current_user
    
    # 获取邀请信息
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT family_id, invitee_username FROM family_invitations WHERE id=%s AND status=%s",
                (action.invitation_id, "pending")
            )
            invitation = await cursor.fetchone()
            
            if not invitation:
                raise HTTPException(status_code=404, detail="邀请不存在或已处理")
            
            family_id = invitation['family_id']
            invitee_username = invitation['invitee_username']
            
            if invitee_username != username:
                raise HTTPException(status_code=403, detail="无权处理此邀请")
            
            if action.action == "accept":
                # 接受邀请，将用户加入家庭
                user_id = await get_user_id_by_username(username)
                await cursor.execute(
                    "INSERT INTO user_families (user_id, family_id, role) VALUES (%s, %s, %s)",
                    (user_id, family_id, "member")
                )
                # 检查用户是否有默认家庭，如果没有则设置为默认家庭
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (user_id,)
                )
                result = await cursor.fetchone()
                if not result or not result['default_family_id']:
                    await cursor.execute(
                        "UPDATE users SET default_family_id=%s WHERE id=%s",
                        (family_id, user_id)
                    )
            
            # 更新邀请状态
            await cursor.execute(
                "UPDATE family_invitations SET status=%s WHERE id=%s",
                (action.action, action.invitation_id)
            )
            
            await conn.commit()
    
    return {"message": f"邀请已{action.action}"}

@user_app.put("/families/default/{family_id}")
async def set_default_family(family_id: str, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户是否是该家庭的成员
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (user_id, family_id)
            )
            if not await cursor.fetchone():
                raise HTTPException(status_code=403, detail="您不是该家庭的成员")
            
            # 设置默认家庭
            await cursor.execute(
                "UPDATE users SET default_family_id=%s WHERE id=%s",
                (family_id, user_id)
            )
            await conn.commit()
    
    return {"message": "默认家庭设置成功"}


@user_app.get("/families/members")
async def get_family_members(family_id: str = None, current_user: str = Depends(get_current_user)):
    """查询家庭中的成员列表
    
    Args:
        family_id: 家庭ID，如果不提供则使用默认家庭
        current_user: 当前登录用户
    """
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 确定要查询的家庭ID
    target_family_id = family_id
    if not target_family_id:
        # 使用默认家庭
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (user_id,)
                )
                result = await cursor.fetchone()
                if not result or not result['default_family_id']:
                    raise HTTPException(status_code=400, detail="用户没有默认家庭")
                target_family_id = result['default_family_id']
    
    # 验证用户是否是该家庭的成员
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (user_id, target_family_id)
            )
            if not await cursor.fetchone():
                raise HTTPException(status_code=403, detail="您不是该家庭的成员")
            
            # 查询家庭成员
            await cursor.execute(
                """
                SELECT u.id, u.username, u.email, u.phone, uf.role 
                FROM users u 
                JOIN user_families uf ON u.id = uf.user_id 
                WHERE uf.family_id = %s
                """,
                (target_family_id,)
            )
            members = await cursor.fetchall()
    
    # 转换为响应格式
    return [
        {
            "id": member['id'],
            "username": member['username'],
            "email": member['email'],
            "phone": member['phone'],
            "role": member['role']
        }
        for member in members
    ]


@user_app.delete("/families/members")
async def remove_family_member(remove_request: RemoveMemberRequest, current_user: str = Depends(get_current_user)):
    """删除家庭成员
    
    要求：
    1. 当前用户必须是家庭的所有者
    2. 不能删除所有者自己
    3. 只能删除其他成员
    
    Args:
        remove_request: 删除请求，包含family_id和member_id
        current_user: 当前登录用户
    """
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 确定要操作的家庭ID
    target_family_id = remove_request.family_id
    if not target_family_id:
        # 使用默认家庭
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (user_id,)
                )
                result = await cursor.fetchone()
                if not result or not result['default_family_id']:
                    raise HTTPException(status_code=400, detail="用户没有默认家庭")
                target_family_id = result['default_family_id']
    
    # 验证当前用户是否是家庭的所有者
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            # 检查当前用户的角色
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (user_id, target_family_id)
            )
            user_role = await cursor.fetchone()
            if not user_role or user_role['role'] != 'owner':
                raise HTTPException(status_code=403, detail="只有家庭所有者才能删除成员")
            
            # 检查要删除的成员是否存在且是该家庭的成员
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (remove_request.member_id, target_family_id)
            )
            member_role = await cursor.fetchone()
            if not member_role:
                raise HTTPException(status_code=404, detail="该用户不是该家庭的成员")
            
            # 不能删除所有者自己
            if remove_request.member_id == user_id:
                raise HTTPException(status_code=400, detail="不能删除家庭所有者自己")
            
            # 执行删除操作
            await cursor.execute(
                "DELETE FROM user_families WHERE user_id=%s AND family_id=%s",
                (remove_request.member_id, target_family_id)
            )
            
            # 检查被删除成员的默认家庭
            await cursor.execute(
                "SELECT default_family_id FROM users WHERE id=%s",
                (remove_request.member_id,)
            )
            user_default_family = await cursor.fetchone()
            
            if user_default_family and user_default_family['default_family_id'] == target_family_id:
                # 默认家庭是当前被删除的家庭，需要更新默认家庭
                # 检查用户是否还有其他家庭
                await cursor.execute(
                    "SELECT family_id FROM user_families WHERE user_id=%s",
                    (remove_request.member_id,)
                )
                remaining_families = await cursor.fetchall()
                
                if remaining_families:
                    # 有其他家庭，随机选取一个作为新的默认家庭
                    new_default_family = remaining_families[0]['family_id']
                    await cursor.execute(
                        "UPDATE users SET default_family_id=%s WHERE id=%s",
                        (new_default_family, remove_request.member_id)
                    )
                else:
                    # 没有其他家庭，将默认家庭置为NULL
                    await cursor.execute(
                        "UPDATE users SET default_family_id=NULL WHERE id=%s",
                        (remove_request.member_id,)
                    )
            
            await conn.commit()
    
    return {"message": "成员删除成功"}


@user_app.put("/families/members/role")
async def update_member_role(update_request: UpdateMemberRoleRequest, current_user: str = Depends(get_current_user)):
    """修改家庭成员角色
    
    要求：
    1. 当前用户必须是家庭的所有者
    2. 可以将成员角色设置为 'owner' 或 'member'
    3. 如果设置为 'owner'，确保家庭至少有一个所有者
    
    Args:
        update_request: 修改角色请求，包含family_id、member_id和role
        current_user: 当前登录用户
    """
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证角色值
    if update_request.role not in ['owner', 'member']:
        raise HTTPException(status_code=400, detail="角色必须是 'owner' 或 'member'")
    
    # 确定要操作的家庭ID
    target_family_id = update_request.family_id
    if not target_family_id:
        # 使用默认家庭
        async with get_db() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT default_family_id FROM users WHERE id=%s",
                    (user_id,)
                )
                result = await cursor.fetchone()
                if not result or not result['default_family_id']:
                    raise HTTPException(status_code=400, detail="用户没有默认家庭")
                target_family_id = result['default_family_id']
    
    # 验证当前用户是否是家庭的所有者
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            # 检查当前用户的角色
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (user_id, target_family_id)
            )
            user_role = await cursor.fetchone()
            if not user_role or user_role['role'] != 'owner':
                raise HTTPException(status_code=403, detail="只有家庭所有者才能修改成员角色")
            
            # 检查要修改的成员是否存在且是该家庭的成员
            await cursor.execute(
                "SELECT role FROM user_families WHERE user_id=%s AND family_id=%s",
                (update_request.member_id, target_family_id)
            )
            member_role = await cursor.fetchone()
            if not member_role:
                raise HTTPException(status_code=404, detail="该用户不是该家庭的成员")
            
            # 如果要将成员角色改为非owner，需要确保家庭至少有一个owner
            if member_role['role'] == 'owner' and update_request.role == 'member':
                await cursor.execute(
                    "SELECT COUNT(*) as count FROM user_families WHERE family_id=%s AND role='owner'",
                    (target_family_id,)
                )
                owner_count = await cursor.fetchone()
                if owner_count['count'] <= 1:
                    raise HTTPException(status_code=400, detail="家庭至少需要有一个所有者")
            
            # 执行角色更新操作
            await cursor.execute(
                "UPDATE user_families SET role=%s WHERE user_id=%s AND family_id=%s",
                (update_request.role, update_request.member_id, target_family_id)
            )
            await conn.commit()
    
    return {"message": f"成员角色已更新为 {update_request.role}"}


@user_app.post("/api-keys", response_model=ApiKeyCreateResponse)
async def create_user_api_key(payload: ApiKeyCreateRequest, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    key_name = (payload.name or "").strip() or "默认 API Key"
    created = await create_api_key_for_user(user_id, key_name)
    return created


@user_app.get("/api-keys", response_model=List[ApiKeyListItem])
async def list_user_api_keys(current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    return await list_api_keys_by_user(user_id)


@user_app.delete("/api-keys/{key_id}")
async def revoke_user_api_key(key_id: str, current_user: str = Depends(get_current_user)):
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    revoked = await revoke_api_key_for_user(user_id, key_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="API Key 不存在或已被吊销")

    return {"message": "API Key 已吊销"}
