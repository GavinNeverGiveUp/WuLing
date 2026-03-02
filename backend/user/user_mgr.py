
# 用户和家庭管理子应用
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, FastAPI, HTTPException

from auth.auth_handler import create_access_token, get_current_user
from db.db_tools import get_db
from schema.models import FamilyCreate, FamilyResponse, MessageResponse, Token, UserCreate, UserLogin, UserResponse, FamilyInvitationCreate, FamilyInvitationResponse, FamilyInvitationAction
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
        
        # 检查用户是否已有默认家庭，如果没有则设置为默认家庭
        cursor.execute(
            "SELECT default_family_id FROM users WHERE id=?",
            (user_id,)
        )
        if not cursor.fetchone()[0]:
            cursor.execute(
                "UPDATE users SET default_family_id=? WHERE id=?",
                (family_id, user_id)
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

@user_app.post("/families/invitations", response_model=FamilyInvitationResponse)
def send_family_invitation(invitation: FamilyInvitationCreate, current_user: str = Depends(get_current_user)):
    inviter_id = get_user_id_by_username(current_user)
    if not inviter_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查被邀请用户是否存在
    invitee = get_user_by_username(invitation.invitee_username)
    if not invitee:
        raise HTTPException(status_code=404, detail="被邀请用户不存在")
    
    # 检查邀请者是否是家庭的成员
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM user_families WHERE user_id=? AND family_id=?",
            (inviter_id, invitation.family_id)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="您不是该家庭的成员")
    
    # 创建邀请
    invitation_id = str(uuid4())
    created_at = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO family_invitations (id, family_id, inviter_id, invitee_username, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (invitation_id, invitation.family_id, inviter_id, invitation.invitee_username, "pending", created_at)
        )
        conn.commit()
    
    return {
        "id": invitation_id,
        "family_id": invitation.family_id,
        "inviter_id": inviter_id,
        "invitee_username": invitation.invitee_username,
        "status": "pending",
        "created_at": created_at
    }

@user_app.get("/families/invitations", response_model=List[FamilyInvitationResponse])
def get_pending_invitations(current_user: str = Depends(get_current_user)):
    username = current_user
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, family_id, inviter_id, invitee_username, status, created_at FROM family_invitations WHERE invitee_username=? AND status=?",
            (username, "pending")
        )
        rows = cursor.fetchall()
    
    return [
        {
            "id": row[0],
            "family_id": row[1],
            "inviter_id": row[2],
            "invitee_username": row[3],
            "status": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]

@user_app.post("/families/invitations/action")
def handle_invitation_action(action: FamilyInvitationAction, current_user: str = Depends(get_current_user)):
    username = current_user
    
    # 获取邀请信息
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT family_id, invitee_username FROM family_invitations WHERE id=? AND status=?",
            (action.invitation_id, "pending")
        )
        invitation = cursor.fetchone()
        
        if not invitation:
            raise HTTPException(status_code=404, detail="邀请不存在或已处理")
        
        family_id, invitee_username = invitation
        
        if invitee_username != username:
            raise HTTPException(status_code=403, detail="无权处理此邀请")
        
        if action.action == "accept":
            # 接受邀请，将用户加入家庭
            user_id = get_user_id_by_username(username)
            cursor.execute(
                "INSERT INTO user_families (user_id, family_id, role) VALUES (?, ?, ?)",
                (user_id, family_id, "member")
            )
            # 检查用户是否有默认家庭，如果没有则设置为默认家庭
            cursor.execute(
                "SELECT default_family_id FROM users WHERE id=?",
                (user_id,)
            )
            if not cursor.fetchone()[0]:
                cursor.execute(
                    "UPDATE users SET default_family_id=? WHERE id=?",
                    (family_id, user_id)
                )
        
        # 更新邀请状态
        cursor.execute(
            "UPDATE family_invitations SET status=? WHERE id=?",
            (action.action, action.invitation_id)
        )
        
        conn.commit()
    
    return {"message": f"邀请已{action.action}"}

@user_app.put("/families/default/{family_id}")
def set_default_family(family_id: str, current_user: str = Depends(get_current_user)):
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户是否是该家庭的成员
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM user_families WHERE user_id=? AND family_id=?",
            (user_id, family_id)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="您不是该家庭的成员")
        
        # 设置默认家庭
        cursor.execute(
            "UPDATE users SET default_family_id=? WHERE id=?",
            (family_id, user_id)
        )
        conn.commit()
    
    return {"message": "默认家庭设置成功"}

