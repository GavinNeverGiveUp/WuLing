from contextlib import asynccontextmanager
import os
import json
import aiomysql
from typing import Optional

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'db': 'family_items',
    'charset': 'utf8mb4',
    'cursorclass': aiomysql.DictCursor
}

# 尝试从环境变量读取JSON格式的配置
if os.getenv('DB_CONFIG'):
    try:
        db_config_json = os.getenv('DB_CONFIG')
        # 移除可能的引号
        if db_config_json.startswith('"') and db_config_json.endswith('"'):
            db_config_json = db_config_json[1:-1]
        # 解析JSON
        config_dict = json.loads(db_config_json)
        # 更新配置
        DB_CONFIG.update(config_dict)
    except json.JSONDecodeError:
        print("警告: DB_CONFIG环境变量格式错误，使用默认配置")

# 连接池
_pool: Optional[aiomysql.Pool] = None

async def init_db_pool():
    """初始化数据库连接池"""
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset'],
            cursorclass=DB_CONFIG['cursorclass'],
            minsize=1,
            maxsize=10,
            autocommit=False
        )
    return _pool

@asynccontextmanager
async def get_db():
    """获取数据库连接的异步上下文管理器"""
    global _pool
    if _pool is None:
        await init_db_pool()
    
    async with _pool.acquire() as conn:
        try:
            yield conn
        except Exception:
            await conn.rollback()
            raise
