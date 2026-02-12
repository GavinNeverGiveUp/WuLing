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

def get_user_by_username(username: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, phone FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3], "phone": row[4]}
    return None

def get_user_id_by_username(username: str) -> Optional[str]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row[0] if row else None
    

def get_user_families(user_id: str) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, f.name 
            FROM families f 
            JOIN user_families uf ON f.id = uf.family_id 
            WHERE uf.user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

def get_default_family(user_id: str) -> Optional[str]:
    families = get_user_families(user_id)
    if len(families) == 1:
        return families[0]["id"]
    return None