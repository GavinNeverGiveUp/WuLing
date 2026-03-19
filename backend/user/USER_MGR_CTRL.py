import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional
from uuid import uuid4

from db.db_tools import get_db


def _hash_with_salt(raw_value: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        raw_value.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return digest.hex()


def _mask_key_preview(prefix: str) -> str:
    if len(prefix) <= 8:
        return f"{prefix}****"

    return f"{prefix[:8]}****{prefix[-4:]}"


def parse_api_key(value: str) -> Optional[tuple[str, str]]:
    if not value or "." not in value:
        return None

    parts = value.split(".", 1)
    if len(parts) != 2:
        return None

    prefix, secret = parts[0].strip(), parts[1].strip()
    if not prefix.startswith("wlk_") or not secret:
        return None

    return prefix, secret


async def create_api_key_for_user(user_id: str, name: str) -> dict:

    key_id = str(uuid4())
    key_prefix = f"wlk_{key_id.replace('-', '')[:24]}"
    key_secret = secrets.token_urlsafe(32)
    plain_key = f"{key_prefix}.{key_secret}"
    salt = secrets.token_hex(16)
    key_hash = _hash_with_salt(key_secret, salt)
    created_at = datetime.now()

    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO api_keys (id, user_id, name, key_prefix, key_hash, salt, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (key_id, user_id, name, key_prefix, key_hash, salt, "active", created_at),
            )
            await conn.commit()

    return {
        "id": key_id,
        "name": name,
        "api_key": plain_key,
        "key_prefix": key_prefix,
        "created_at": created_at.isoformat(),
    }


async def list_api_keys_by_user(user_id: str) -> list[dict]:

    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT id, name, key_prefix, status, created_at, last_used_at
                FROM api_keys
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = await cursor.fetchall()

    result = []
    for row in rows:
        created_at = row.get("created_at")
        last_used_at = row.get("last_used_at")
        result.append(
            {
                "id": row["id"],
                "name": row["name"],
                "key_prefix": row["key_prefix"],
                "key_preview": _mask_key_preview(row["key_prefix"]),
                "status": row["status"],
                "created_at": created_at.isoformat() if created_at else "",
                "last_used_at": last_used_at.isoformat() if last_used_at else None,
            }
        )

    return result


async def revoke_api_key_for_user(user_id: str, key_id: str) -> bool:

    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE api_keys
                SET status = 'revoked', revoked_at = %s
                WHERE id = %s AND user_id = %s AND status = 'active'
                """,
                (datetime.now(), key_id, user_id),
            )
            updated = cursor.rowcount
            await conn.commit()

    return updated > 0


async def get_username_by_api_key(api_key: str, client_ip: Optional[str] = None) -> Optional[str]:

    parsed = parse_api_key(api_key)
    if not parsed:
        return None

    key_prefix, key_secret = parsed

    async with get_db() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT ak.id, ak.salt, ak.key_hash, ak.status, u.username
                FROM api_keys ak
                JOIN users u ON u.id = ak.user_id
                WHERE ak.key_prefix = %s
                LIMIT 1
                """,
                (key_prefix,),
            )
            row = await cursor.fetchone()
            if not row:
                return None

            expected_hash = row["key_hash"]
            calculated_hash = _hash_with_salt(key_secret, row["salt"])
            if not hmac.compare_digest(expected_hash, calculated_hash):
                return None

            if row["status"] != "active":
                return None

            await cursor.execute(
                "UPDATE api_keys SET last_used_at = %s, last_used_ip = %s WHERE id = %s",
                (datetime.now(), client_ip, row["id"]),
            )
            await conn.commit()

            return row["username"]
