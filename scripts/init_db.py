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
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            create_time TEXT NOT NULL,
            default_family_id TEXT,
            FOREIGN KEY (default_family_id) REFERENCES families(id)
        )
    ''')
    
    # 家庭表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS families (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    # 用户家庭关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_families (
            user_id TEXT,
            family_id TEXT,
            role TEXT DEFAULT 'member',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (family_id) REFERENCES families(id)
        )
    ''')
    
    # 家庭邀请表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_invitations (
            id TEXT PRIMARY KEY,
            family_id TEXT,
            inviter_id TEXT,
            invitee_username TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            FOREIGN KEY (family_id) REFERENCES families(id),
            FOREIGN KEY (inviter_id) REFERENCES users(id)
        )
    ''')
    
    # 物品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT NOT NULL,
            family_id TEXT,
            added_by TEXT,
            created_at TEXT,
            expiration_date TEXT,
            FOREIGN KEY (family_id) REFERENCES families(id),
            FOREIGN KEY (added_by) REFERENCES users(id)
        )
    ''')

    # 用户会话历史表
    cursor.execute('''
       drop table if exists messages;
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