from contextlib import asynccontextmanager
import json
import logging
import os
import time

import aiomysql


logger = logging.getLogger(__name__)

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
        logger.warning("db_config_parse_failed_use_default")


@asynccontextmanager
async def get_db():
    """获取数据库连接的异步上下文管理器（单连接模式）"""
    conn = None
    connect_start = time.perf_counter()

    try:
        # 创建新的数据库连接
        conn = await aiomysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset'],
            cursorclass=DB_CONFIG['cursorclass'],
            autocommit=False
        )
    except Exception as connect_error:
        logger.exception(
            "db_connect_failed",
            extra={
                "stage": "connect",
                "error_type": type(connect_error).__name__,
                "db_host": DB_CONFIG['host'],
                "db_name": DB_CONFIG['db'],
            },
        )
        raise

    connect_latency_ms = round((time.perf_counter() - connect_start) * 1000, 2)
    if connect_latency_ms >= 200:
        logger.warning(
            "db_connect_slow",
            extra={
                "stage": "connect",
                "latency_ms": connect_latency_ms,
                "db_host": DB_CONFIG['host'],
                "db_name": DB_CONFIG['db'],
            },
        )

    try:
        yield conn
    except Exception as context_error:
        logger.exception(
            "db_context_failed",
            extra={
                "stage": "context",
                "error_type": type(context_error).__name__,
                "db_host": DB_CONFIG['host'],
                "db_name": DB_CONFIG['db'],
            },
        )
        try:
            await conn.rollback()
        except Exception as rollback_error:
            logger.warning(
                "db_rollback_failed",
                extra={
                    "stage": "rollback",
                    "error": str(rollback_error),
                    "error_type": type(rollback_error).__name__,
                },
            )
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as close_error:
                logger.warning(
                    "db_close_failed",
                    extra={
                        "stage": "close",
                        "error": str(close_error),
                        "error_type": type(close_error).__name__,
                    },
                )
