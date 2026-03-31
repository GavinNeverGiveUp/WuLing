# 辅助函数
import hashlib
import secrets
from typing import List, Optional
from db.db_tools import get_db
from setting import pwd_context

def generate_salt():
    return secrets.token_hex(16)

def get_password_hash(password: str, salt: str = None) -> str:
    if salt is None:
        salt = generate_salt()
    # 使用sha256 + salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  password.encode('utf-8'), 
                                  salt.encode('utf-8'), 
                                  100000)
    return salt + pwdhash.hex()

def verify_password(plain_password: str, stored_hash: str) -> bool:
    salt = stored_hash[:32]  # 取前32个字符作为salt
    stored_pwd = stored_hash[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256',
                                  plain_password.encode('utf-8'),
                                  salt.encode('utf-8'),
                                  100000)
    return pwdhash.hex() == stored_pwd


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

async def get_user_by_username(username: str) -> Optional[dict]:
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id, username, email, password_hash, phone FROM users WHERE username = %s", (username,))
            row = await cursor.fetchone()
            if row:
                return {"id": row['id'], "username": row['username'], "email": row['email'], "password_hash": row['password_hash'], "phone": row['phone']}
    return None

async def get_user_id_by_username(username: str) -> Optional[str]:
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            row = await cursor.fetchone()
            return row['id'] if row else None
    

async def get_user_families(user_id: str) -> List[dict]:
    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    f.id,
                    f.name,
                    uf.role,
                    CASE WHEN u.default_family_id = f.id THEN TRUE ELSE FALSE END AS is_default
                FROM families f
                JOIN user_families uf ON f.id = uf.family_id
                JOIN users u ON u.id = uf.user_id
                WHERE uf.user_id = %s
                ORDER BY is_default DESC, f.name ASC
            """, (user_id,))
            rows = await cursor.fetchall()
            return [
                {
                    "id": row['id'],
                    "name": row['name'],
                    "role": row.get('role'),
                    "is_default": bool(row.get('is_default'))
                }
                for row in rows
            ]

async def get_default_family(user_id: str) -> Optional[str]:
    families = await get_user_families(user_id)
    if len(families) == 1:
        return families[0]["id"]
    return None
