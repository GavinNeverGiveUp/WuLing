import os
import sqlite3

def get_db_path():
    """获取数据库文件的绝对路径"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(current_dir, 'family_items.db')
    return os.path.abspath(db_path)

# 创建数据库表
def create_tables():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 用户会话历史表
    cursor.execute('''
       drop table if exists messages
    ''')
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    tool_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
    ''')
    
    conn.commit()
    conn.close()

if "__main__" == __name__:
    create_tables()