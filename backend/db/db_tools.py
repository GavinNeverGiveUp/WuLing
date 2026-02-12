from contextlib import contextmanager
import os
import sqlite3


def get_db_path():
    """获取数据库文件的绝对路径"""
    # 获取当前文件所在目录的父目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, '..', '..', 'family_items.db')
    return os.path.abspath(db_path)

@contextmanager
def get_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)  # 打开数据库连接
    try:
        yield conn  # 返回连接供使用
    finally:
        conn.close()  # 确保连接被关闭